import re
from typing import Any


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


AGE_GROUPS = {
    "13-18": (13, 18),
    "20-30": (20, 30),
    "30+": (30, 120),
}

OBJECTIVES = {
    "weight_loss": "Perda de peso",
    "muscle_gain": "Ganho de massa muscular",
    "strength_gain": "Aumento de força",
}


def sanitize_text(value: Any, max_length: int = 120) -> str:
    """Strip unsafe characters and normalize input strings."""
    if value is None:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", str(value)).strip()
    return cleaned[:max_length]


def is_weight_valid(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return 10 <= number <= 100


def is_age_group_valid(value: Any) -> bool:
    return value in AGE_GROUPS


def is_objective_valid(value: Any) -> bool:
    return value in OBJECTIVES


def is_valid_email(value: Any) -> bool:
    if value is None:
        return False
    return bool(EMAIL_PATTERN.fullmatch(sanitize_text(value, 254)))


def validate_payload(payload: dict[str, Any]) -> tuple[bool, dict[str, str]]:
    """Validate the incoming form payload."""
    errors: dict[str, str] = {}

    age_group = sanitize_text(payload.get("age_group"))
    current_weight = payload.get("current_weight")
    desired_weight = payload.get("desired_weight")
    objective = sanitize_text(payload.get("objective"))

    if not is_age_group_valid(age_group):
        errors["age_group"] = "Selecione uma faixa de idade válida."

    if not is_weight_valid(current_weight):
        errors["current_weight"] = "Informe um peso atual entre 10 kg e 100 kg."

    if not is_weight_valid(desired_weight):
        errors["desired_weight"] = "Informe um peso desejado entre 10 kg e 100 kg."

    if not is_objective_valid(objective):
        errors["objective"] = "Selecione um objetivo válido."

    if is_weight_valid(current_weight) and is_weight_valid(desired_weight):
        current = float(current_weight)
        desired = float(desired_weight)
        if abs(current - desired) < 1.5:
            errors["desired_weight"] = "O peso desejado deve diferir do atual para gerar uma estimativa útil."

    if age_group == "13-18" and objective == "weight_loss" and abs(float(current_weight) - float(desired_weight)) > 15:
        errors["desired_weight"] = "Para menores de 18 anos, priorizamos metas de saúde e progresso gradual, sem restrições extremas."

    return (len(errors) == 0, errors)
