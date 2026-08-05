from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "gymforus.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            sex TEXT,
            age INTEGER,
            height_cm INTEGER,
            experience_level TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            objective TEXT NOT NULL,
            objective_label TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            plan_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()
    conn.close()


def create_user(username: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), generate_password_hash(password)),
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        return True, "", {"id": user_id, "username": username.strip(), "email": email.strip().lower()}
    except sqlite3.IntegrityError as exc:
        if "users.username" in str(exc):
            return False, "Nome de usuário já cadastrado.", None
        return False, "E-mail já cadastrado.", None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> dict | None:
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, email, password_hash FROM users WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    conn.close()

    if user is None:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
    }


def upsert_user_profile(user_id: int, profile: dict) -> dict:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO user_profiles (user_id, full_name, sex, age, height_cm, experience_level)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            full_name = excluded.full_name,
            sex = excluded.sex,
            age = excluded.age,
            height_cm = excluded.height_cm,
            experience_level = excluded.experience_level,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            user_id,
            profile.get("full_name"),
            profile.get("sex"),
            profile.get("age"),
            profile.get("height_cm"),
            profile.get("experience_level"),
        ),
    )
    conn.commit()
    conn.close()
    return get_user_profile(user_id) or {}


def get_user_profile(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT full_name, sex, age, height_cm, experience_level, updated_at FROM user_profiles WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "full_name": row["full_name"],
        "sex": row["sex"],
        "age": row["age"],
        "height_cm": row["height_cm"],
        "experience_level": row["experience_level"],
        "updated_at": row["updated_at"],
    }


def save_user_plan(user_id: int, objective: str, objective_label: str, metrics: dict, plan: dict) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO plans (user_id, objective, objective_label, metrics_json, plan_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            objective,
            objective_label,
            json.dumps(metrics, ensure_ascii=False),
            json.dumps(plan, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()


def get_user_history(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, objective, objective_label, metrics_json, plan_json, created_at
        FROM plans
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 8
        """,
        (user_id,),
    ).fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append(
            {
                "id": row["id"],
                "objective": row["objective"],
                "objective_label": row["objective_label"],
                "metrics": json.loads(row["metrics_json"]),
                "plan": json.loads(row["plan_json"]),
                "created_at": row["created_at"],
            }
        )
    return history


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()

    if row is None:
        return None
    return {"id": row["id"], "username": row["username"], "email": row["email"]}
