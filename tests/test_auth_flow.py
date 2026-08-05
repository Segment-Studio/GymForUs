import os
import unittest

from backend.app import app
from backend.database import DB_PATH, init_db


class AuthFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        if DB_PATH.exists():
            DB_PATH.unlink()
        self.client = app.test_client()
        app.config.update(TESTING=True)
        init_db()

    def test_register_login_generate_and_dashboard(self) -> None:
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongPass123",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "StrongPass123"},
        )
        self.assertEqual(login_response.status_code, 200)

        profile_response = self.client.put(
            "/api/profile",
            json={
                "full_name": "Test User",
                "sex": "female",
                "age": 27,
                "height_cm": 168,
                "experience_level": "intermediate",
            },
        )
        self.assertEqual(profile_response.status_code, 200)

        plan_response = self.client.post(
            "/api/generate",
            json={
                "age_group": "20-30",
                "current_weight": "70",
                "desired_weight": "68",
                "objective": "weight_loss",
            },
        )
        self.assertEqual(plan_response.status_code, 200)
        self.assertIn("profile_summary", plan_response.get_json()["result"])

        dashboard_response = self.client.get("/dashboard")
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn("Test User", dashboard_response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
