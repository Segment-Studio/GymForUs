from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_cors import CORS

from ai.plan_generator import build_ai_response
from backend.database import (
    authenticate_user,
    create_user,
    get_user_by_id,
    get_user_history,
    get_user_profile,
    init_db,
    save_user_plan,
    upsert_user_profile,
)
from config.settings import Settings
from utils.calculations import estimate_daily_metrics
from utils.validators import is_valid_email, sanitize_text, validate_payload


BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

logging.basicConfig(level=logging.INFO)

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR / "static"),
)

settings = Settings()
allowed_origins = list(settings.CORS_ALLOWED_ORIGINS)
for host in ("127.0.0.1", "localhost", "0.0.0.0"):
    for port in ("5000", "8000", "3000"):
        allowed_origins.append(f"http://{host}:{port}")
        allowed_origins.append(f"https://{host}:{port}")
if settings.HOST not in {"0.0.0.0", "127.0.0.1", "localhost"}:
    allowed_origins.append(f"https://{settings.HOST}")
allowed_origins = [origin for origin in dict.fromkeys(allowed_origins)]
CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins, "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}},
    supports_credentials=True,
)

app.config.update(
    SECRET_KEY=settings.SECRET_KEY,
    MAX_CONTENT_LENGTH=1024 * 1024,
    PROPAGATE_EXCEPTIONS=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=settings.SESSION_COOKIE_SECURE,
    JSON_SORT_KEYS=False,
)

init_db()

rate_limit_store: dict[str, list[float]] = defaultdict(list)


def parse_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def is_rate_limited(endpoint: str) -> bool:
    now = monotonic()
    window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS
    key = f"{endpoint}:{request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0]}"
    hits = rate_limit_store[key]
    hits[:] = [timestamp for timestamp in hits if now - timestamp < window_seconds]
    if len(hits) >= settings.RATE_LIMIT_REQUESTS:
        return True
    hits.append(now)
    return False


def normalize_origin(origin: str | None) -> str:
    if not origin:
        return ""
    parsed = urlsplit(origin.strip())
    if not parsed.scheme or not parsed.hostname:
        return origin.strip().rstrip("/").lower()
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme.lower()}://{parsed.hostname.lower()}{port}".rstrip("/")


def is_origin_allowed() -> bool:
    origin = request.headers.get("Origin")
    if not origin:
        return True
    normalized_origin = normalize_origin(origin)
    normalized_allowed = {normalize_origin(candidate) for candidate in allowed_origins}
    return normalized_origin in normalized_allowed


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin and is_origin_allowed():
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.after_request
def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' https://images.unsplash.com data:; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self'; "
        "connect-src 'self'"
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(400)
def handle_bad_request(_error):
    return jsonify({"error": "Solicitação inválida."}), 400


@app.errorhandler(404)
def handle_not_found(_error):
    return jsonify({"error": "Recurso não encontrado."}), 404


@app.errorhandler(429)
def handle_rate_limit(_error):
    return jsonify({"error": "Muitas tentativas. Tente novamente mais tarde."}), 429


@app.errorhandler(500)
def handle_server_error(_error):
    return jsonify({"error": "Não foi possível concluir a solicitação no momento."}), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unhandled exception", exc_info=error)
    return jsonify({"error": "Ocorreu um erro inesperado. Tente novamente em instantes."}), 500


@app.route("/api/<path:path>", methods=["OPTIONS"])
def api_options(path):
    origin = request.headers.get("Origin")
    response = jsonify({})
    if origin and is_origin_allowed():
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response, 200


@app.get("/")
def home_page():
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = get_user_by_id(user_id)
    return render_template("index.html", user=user)


@app.get("/dashboard")
def dashboard_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("home_page"))

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for("home_page"))

    history = get_user_history(user_id)
    profile = get_user_profile(user_id)
    return render_template("dashboard.html", user=user, history=history, profile=profile)


@app.get("/health")
def health_check():
    return jsonify({"status": "ok", "app": settings.APP_NAME})


@app.get("/api/auth/me")
def auth_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False})

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"authenticated": False})

    return jsonify({"authenticated": True, "user": user})


@app.get("/api/profile")
def get_profile_api():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False})

    user = get_user_by_id(user_id)
    profile = get_user_profile(user_id)
    return jsonify({"authenticated": True, "user": user, "profile": profile})


@app.put("/api/profile")
def update_profile_api():
    if is_rate_limited("profile"):
        return jsonify({"error": "Muitas tentativas. Tente novamente mais tarde."}), 429
    if request.headers.get("Origin") and not is_origin_allowed():
        return jsonify({"error": "Origem não permitida."}), 403

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Autenticação necessária."}), 401

    payload = request.get_json(silent=True) or {}
    full_name = sanitize_text(payload.get("full_name"), 80)
    sex = sanitize_text(payload.get("sex"))
    experience_level = sanitize_text(payload.get("experience_level"))

    age = parse_int(payload.get("age"))
    height_cm = parse_int(payload.get("height_cm"))
    if age is None or height_cm is None:
        return jsonify({"error": "Idade e altura devem ser números válidos."}), 400

    errors: dict[str, str] = {}
    if not full_name:
        errors["full_name"] = "Informe seu nome completo."
    if sex not in {"male", "female", "other"}:
        errors["sex"] = "Selecione um sexo válido."
    if not 13 <= age <= 100:
        errors["age"] = "Informe uma idade válida."
    if not 120 <= height_cm <= 240:
        errors["height_cm"] = "Informe uma altura válida."
    if experience_level not in {"beginner", "intermediate", "advanced"}:
        errors["experience_level"] = "Selecione um nível de experiência válido."

    if errors:
        return jsonify({"error": "Dados inválidos", "details": errors}), 400

    profile = upsert_user_profile(
        user_id,
        {
            "full_name": full_name,
            "sex": sex,
            "age": age,
            "height_cm": height_cm,
            "experience_level": experience_level,
        },
    )
    return jsonify({"success": True, "profile": profile})


@app.post("/api/auth/register")
def register_user():
    if is_rate_limited("register"):
        return jsonify({"error": "Muitas tentativas. Tente novamente mais tarde."}), 429
    if request.headers.get("Origin") and not is_origin_allowed():
        return jsonify({"error": "Origem não permitida."}), 403

    payload = request.get_json(silent=True) or {}
    username = sanitize_text(payload.get("username"), 40)
    email = sanitize_text(payload.get("email"), 254)
    password = payload.get("password")

    if not username or not is_valid_email(email) or not isinstance(password, str) or len(password) < 6:
        return jsonify({"error": "Informe um nome válido, um e-mail correto e uma senha com pelo menos 6 caracteres."}), 400

    success, message, user_data = create_user(username, email, password)
    if not success or user_data is None:
        return jsonify({"error": message or "Não foi possível criar a conta."}), 400

    session.clear()
    session["user_id"] = user_data["id"]
    return jsonify({"success": True, "message": "Conta criada com sucesso.", "user": user_data}), 201


@app.post("/api/auth/login")
def login_user():
    if is_rate_limited("login"):
        return jsonify({"error": "Muitas tentativas. Tente novamente mais tarde."}), 429
    if request.headers.get("Origin") and not is_origin_allowed():
        return jsonify({"error": "Origem não permitida."}), 403

    payload = request.get_json(silent=True) or {}
    email = sanitize_text(payload.get("email"), 254)
    password = payload.get("password")

    if not is_valid_email(email) or not isinstance(password, str) or len(password) < 1:
        return jsonify({"error": "Informe um e-mail válido e a senha."}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Credenciais inválidas."}), 401

    session.clear()
    session["user_id"] = user["id"]
    return jsonify({"success": True, "message": "Login realizado com sucesso.", "user": user})


@app.post("/api/auth/logout")
def logout_user():
    session.clear()
    return jsonify({"success": True, "message": "Logout realizado."})


@app.post("/api/generate")
def generate_plan():
    if is_rate_limited("generate"):
        return jsonify({"error": "Muitas tentativas. Tente novamente mais tarde."}), 429
    if request.headers.get("Origin") and not is_origin_allowed():
        return jsonify({"error": "Origem não permitida."}), 403

    try:
        payload = request.get_json(silent=True)

        if payload is None or not isinstance(payload, dict):
            return jsonify({"error": "Payload inválido."}), 400

        sanitized_payload = {
            "age_group": sanitize_text(payload.get("age_group")),
            "current_weight": payload.get("current_weight"),
            "desired_weight": payload.get("desired_weight"),
            "objective": sanitize_text(payload.get("objective")),
        }

        is_valid, errors = validate_payload(sanitized_payload)
        if not is_valid:
            return jsonify({"error": "Dados inválidos", "details": errors}), 400

        user_id = session.get("user_id")
        profile = get_user_profile(user_id) if user_id else None
        metrics = estimate_daily_metrics(sanitized_payload)
        response = build_ai_response(sanitized_payload, metrics, profile)

        saved = False
        if user_id:
            try:
                save_user_plan(user_id, response["objective"], response["objective_label"], metrics, response)
                saved = True
            except Exception:
                saved = False

        return jsonify({"success": True, "result": response, "metrics": metrics, "saved": saved})
    except Exception as error:
        app.logger.exception("Plan generation failed", exc_info=error)
        return jsonify({"error": "Não foi possível gerar o plano no momento. Tente novamente em alguns instantes."}), 500


if __name__ == "__main__":
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
