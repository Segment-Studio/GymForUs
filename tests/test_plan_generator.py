import unittest
from pathlib import Path

from ai.plan_generator import build_ai_response


class TestPlanGenerator(unittest.TestCase):
    def test_returns_structured_and_safe_response(self):
        profile = {
            "age_group": "20-30",
            "current_weight": 70,
            "desired_weight": 68,
            "objective": "weight_loss",
        }
        metrics = {
            "daily_calories": 1703,
            "protein": 126,
            "carbs": 168,
            "fats": 56,
            "water_liters": 2.5,
            "time_to_goal_months": 3,
        }

        result = build_ai_response(profile, metrics)

        self.assertIn("objective_label", result)
        self.assertIn("weekly_rest_time", result)
        self.assertIn("responsibility_note", result)
        self.assertTrue(any("estimativas" in item.lower() for item in result["observacoes"]))

    def test_minor_profile_avoids_extreme_or_body_pressure_language(self):
        profile = {
            "age_group": "13-18",
            "current_weight": 62,
            "desired_weight": 54,
            "objective": "weight_loss",
        }
        metrics = {
            "daily_calories": 1800,
            "protein": 87,
            "carbs": 190,
            "fats": 58,
            "water_liters": 2.4,
            "time_to_goal_months": 4,
        }

        result = build_ai_response(profile, metrics)

        self.assertIn("saúde", result["objective_label"].lower())
        self.assertTrue(any("hidratação" in item.lower() or "sono" in item.lower() for item in result["dicas"]))
        self.assertTrue(any("avaliação profissional" in item.lower() or "profissional" in item.lower() for item in result["observacoes"]))

    def test_project_has_gitignore_for_sensitive_files(self):
        self.assertTrue(Path(".gitignore").exists())


if __name__ == "__main__":
    unittest.main()
