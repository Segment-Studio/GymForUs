from __future__ import annotations

from typing import Any


def estimate_daily_metrics(profile: dict[str, Any]) -> dict[str, Any]:
    """Estimate calories and macros using a conservative nutrition reference model."""
    age_group = profile["age_group"]
    current_weight = float(profile["current_weight"])
    desired_weight = float(profile["desired_weight"])
    objective = profile["objective"]

    age_factor = {"13-18": 1.05, "20-30": 1.0, "30+": 0.95}[age_group]
    weight_diff = abs(current_weight - desired_weight)

    # Mifflin-St Jeor inspired baseline estimate for a moderate sedentary-to-lightly-active profile.
    bmr = (10 * current_weight) + (6.25 * 170) - (5 * 28) + 5
    activity_factor = 1.2
    base_calories = bmr * activity_factor * age_factor

    if objective == "weight_loss":
        daily_calories = base_calories - 250
        protein = 1.8 * current_weight
        carbs = 2.4 * current_weight
        fats = 0.8 * current_weight
    elif objective == "muscle_gain":
        daily_calories = base_calories + 220
        protein = 2.0 * current_weight
        carbs = 3.6 * current_weight
        fats = 0.9 * current_weight
    else:
        daily_calories = base_calories + 120
        protein = 1.9 * current_weight
        carbs = 3.1 * current_weight
        fats = 0.85 * current_weight

    hydration_liters = round(0.035 * current_weight, 1)
    approx_months = max(2, round(weight_diff / 0.6))

    return {
        "daily_calories": int(round(daily_calories)),
        "protein": int(round(protein)),
        "carbs": int(round(carbs)),
        "fats": int(round(fats)),
        "water_liters": hydration_liters,
        "time_to_goal_months": approx_months,
        "goal_gap": round(weight_diff, 1),
    }
