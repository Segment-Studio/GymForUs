from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from config.settings import Settings


settings = Settings()

OBJECTIVE_LABELS = {
    "weight_loss": "Perda de peso",
    "muscle_gain": "Ganho de massa muscular",
    "strength_gain": "Aumento de força",
}

EXPERIENCE_LABELS = {
    "beginner": "iniciante",
    "intermediate": "intermediário",
    "advanced": "avançado",
}

DAY_LABELS = {
    "segunda-feira": "SEGUNDA",
    "terça-feira": "TERÇA",
    "quarta-feira": "QUARTA",
    "quinta-feira": "QUINTA",
    "sexta-feira": "SEXTA",
    "sábado": "SÁBADO",
}


def _is_minor(age_group: str) -> bool:
    return age_group == "13-18"


def _build_fallback_response(profile: dict[str, Any], metrics: dict[str, Any], user_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    objective = profile["objective"]
    desired_weight = float(profile["desired_weight"])
    current_weight = float(profile["current_weight"])
    weight_delta = desired_weight - current_weight
    age_group = str(profile.get("age_group", ""))
    is_minor = _is_minor(age_group)
    objective_label = OBJECTIVE_LABELS.get(objective, objective.replace("_", " "))

    experience_level = (user_profile or {}).get("experience_level", "beginner")
    sex = (user_profile or {}).get("sex") or "other"
    age = (user_profile or {}).get("age")
    height_cm = (user_profile or {}).get("height_cm")
    full_name = (user_profile or {}).get("full_name")

    if is_minor:
        objective_label = "Saúde, hábitos e movimento"
        if objective == "weight_loss":
            focus = "Priorize hábitos sustentáveis, hidratação, sono adequado e alimentação equilibrada. Evite restrições extremas ou comparação com o corpo de outras pessoas."
            weekly_rest_time = "2 a 3 dias de recuperação leve por semana"
            sets_label = "2 a 3 séries"
            cardio_focus = "caminhada leve"
        elif objective == "muscle_gain":
            focus = "Priorize aprendizagem da técnica, boa recuperação e alimentação equilibrada para crescimento e desempenho saudável."
            weekly_rest_time = "1 a 2 dias de recuperação leve por semana"
            sets_label = "2 a 3 séries"
            cardio_focus = "bike leve"
        else:
            focus = "Priorize general fitness, técnica segura, movimento consistente e atenção à recuperação."
            weekly_rest_time = "1 a 2 dias de recuperação leve por semana"
            sets_label = "2 a 3 séries"
            cardio_focus = "caminhada leve"
    elif objective == "weight_loss":
        focus = "Priorize déficit moderado, hidratação e sono consistente."
        weekly_rest_time = "2 a 3 dias de descanso leve por semana"
        sets_label = "3 séries"
        cardio_focus = "caminhada de 10 minutos"
    elif objective == "muscle_gain":
        focus = "Priorize recuperação, proteína distribuída ao longo do dia e progressão gradual."
        weekly_rest_time = "1 a 2 dias de recuperação ativa por semana"
        sets_label = "4 séries"
        cardio_focus = "bike leve"
    else:
        focus = "Priorize técnica, esforço controlado e consistência semanal."
        weekly_rest_time = "1 dia de descanso total por semana"
        sets_label = "4 séries"
        cardio_focus = "elíptico leve"

    if experience_level == "advanced":
        rest_label = "1 min ou 2 min"
        rep_label = "6–10 rep"
    elif experience_level == "intermediate":
        rest_label = "1 min ou 2 min"
        rep_label = "8–12 rep"
    else:
        rest_label = "1 min ou 2 min"
        rep_label = "10–12 rep"

    if sex == "female":
        lower_body_focus = "Pernas + glúteos"
        upper_body_focus = "Peito + ombros"
    else:
        lower_body_focus = "Pernas + core"
        upper_body_focus = "Peito + ombros"

    routine = {
        "segunda-feira": {"muscle_group": lower_body_focus, "exercise": "Agachamento goblet, leg press, ponte de glúteo e step-up", "sets": sets_label, "reps": rep_label, "rest": rest_label, "cardio": f"{cardio_focus} por 8 min"},
        "terça-feira": {"muscle_group": upper_body_focus, "exercise": "Supino reto, desenvolvimento militar, flexão assistida e elevação lateral", "sets": sets_label, "reps": rep_label, "rest": rest_label, "cardio": "Bike leve por 8 min"},
        "quarta-feira": {"muscle_group": "Costas + braços", "exercise": "Remada baixa, puxada na polia, rosca direta e tríceps na corda", "sets": sets_label, "reps": rep_label, "rest": rest_label, "cardio": "Caminhada leve por 7 min"},
        "quinta-feira": {"muscle_group": lower_body_focus, "exercise": "Levantamento terra, extensão de pernas, hip thrust e panturrilha", "sets": sets_label, "reps": rep_label, "rest": rest_label, "cardio": "Elíptico leve por 6 min"},
        "sexta-feira": {"muscle_group": "Treino total + mobilidade", "exercise": "Circuito com kettlebell, prancha, remo e mobilidade articular", "sets": "3 séries", "reps": "10–15 rep", "rest": rest_label, "cardio": "Mobilidade e caminhada por 8 min"},
        "sábado": {"muscle_group": "Recuperação ativa", "exercise": "Caminhada, alongamento e mobilidade articular", "sets": "1 bloco", "reps": "20–30 min", "rest": "Sem esforço", "cardio": "Caminhada leve"},
    }

    meal_plan = {
        "Café da manhã": "Iogurte com frutas, aveia e uma fonte de proteína",
        "Almoço": "Carboidrato moderado + proteína + salada + gorduras boas",
        "Lanche da tarde": "Barra da manhã ou smoothie com frutas",
        "Jantar": "Proteína magra + legumes + arroz ou batata",
    }

    profile_summary_parts: list[str] = []
    if full_name:
        profile_summary_parts.append(full_name)
    if age is not None:
        profile_summary_parts.append(f"{age} anos")
    if height_cm is not None:
        profile_summary_parts.append(f"{height_cm} cm")
    if experience_level in EXPERIENCE_LABELS:
        profile_summary_parts.append(EXPERIENCE_LABELS[experience_level])

    profile_summary = " · ".join(profile_summary_parts) if profile_summary_parts else "Perfil geral"
    recommendation = (
        f"Seu objetivo aponta para {objective_label}. "
        f"A meta de peso sugerida está {abs(weight_delta):.1f} kg distante do atual. "
        f"{focus}"
    )

    safety_recommendations = [
        "Mantenha a rotina simples: treino regular, sono adequado e hidratação consistente são os pilares desse plano.",
        "Use a progressão como guia e evite mudanças extremas que comprometam a recuperação.",
        "Distribua a proteína ao longo do dia para melhorar o ganho de massa ou a preservação muscular.",
    ]
    if is_minor:
        safety_recommendations = [
            "Priorize alimentação equilibrada, hidratação e descanso em vez de qualquer restrição extrema.",
            "Foque em saúde, consistência e técnica segura em vez de comparação com o corpo de outras pessoas.",
            "Sempre busque orientação de um profissional de saúde ou educação física para ajustes mais específicos.",
        ]

    return {
        "objective": objective,
        "objective_label": objective_label,
        "weekly_rest_time": weekly_rest_time,
        "plan_alimentar": meal_plan,
        "plano_treino": routine,
        "calorias_diarias": metrics["daily_calories"],
        "proteinas": metrics["protein"],
        "carboidratos": metrics["carbs"],
        "gorduras": metrics["fats"],
        "agua": f"{metrics['water_liters']} L",
        "tempo_estimado": f"{metrics['time_to_goal_months']} meses",
        "profile_summary": profile_summary,
        "recomendacoes": [
            recommendation,
            *safety_recommendations,
        ],
        "dicas": [
            "Ajuste a intensidade conforme sua recuperação e tolerância individual.",
            "Avalie o avanço semanalmente com poucos indicadores: peso, energia, sono e consistência.",
            "Se houver dor intensa ou exaustão, reduza a carga e busque orientação profissional.",
        ],
        "habitos": [
            "Caminhe 10 minutos após as refeições para melhorar o controle do apetite.",
            "Mantenha o ambiente de treino organizado e sem distrações.",
            "Registre peso, hidratação e fome ao longo da semana para compreender melhor a resposta.",
        ],
        "observacoes": [
            "Estas são estimativas baseadas em referências nutricionais gerais e não substituem avaliação profissional.",
            "Qualquer mudança na rotina deve ser feita com atenção à tolerância individual e à recuperação.",
            "Para menores de 18 anos, priorizamos educação saudável, hidratação, sono, recuperação e técnica segura.",
        ],
        "responsibility_note": "Estas estimativas são orientativas e não garantem resultados. Nunca prometa transformação rápida e mantenha uma abordagem segura, realista e gradual. Para menores de 18 anos, o foco deve estar em saúde e hábitos consistentes, não em restrição extrema.",
    }


def _try_external_ai(profile: dict[str, Any], metrics: dict[str, Any], user_profile: dict[str, Any] | None = None) -> dict[str, Any] | None:
    api_url = settings.AI_API_URL.strip()
    api_key = settings.AI_API_KEY.strip()
    if not api_url or not api_key:
        return None

    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Responda exclusivamente com um JSON válido contendo um plano de treino e alimentação seguro, sem incluir markdown."
            },
            {
                "role": "user",
                "content": json.dumps({"profile": profile, "metrics": metrics, "user_profile": user_profile or {}}),
            },
        ],
        "timeout": settings.AI_TIMEOUT_SECONDS,
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.AI_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    if isinstance(data, dict):
        message_content = data.get("choices", [{}])[0].get("message", {}).get("content") if isinstance(data.get("choices"), list) else None
        if isinstance(message_content, str):
            try:
                parsed = json.loads(message_content)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                return None
        if isinstance(data.get("plan"), dict):
            return data["plan"]
    return None


def build_ai_response(profile: dict[str, Any], metrics: dict[str, Any], user_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate a structured, safety-oriented plan with optional external AI fallback."""
    if settings.AI_PROVIDER != "rule-based" and settings.AI_FALLBACK_ENABLED:
        external_plan = _try_external_ai(profile, metrics, user_profile)
        if isinstance(external_plan, dict) and external_plan:
            return external_plan

    fallback = _build_fallback_response(profile, metrics, user_profile)
    fallback["ai_mode"] = "rule-based"
    return fallback
