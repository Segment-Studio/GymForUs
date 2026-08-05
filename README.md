# GymForUs

GymForUs is a fitness planning platform that combines profile-based planning, user accounts, secure backend logic, and a rule-based AI flow for workout and nutrition guidance. The app keeps a clean SaaS-style experience while providing safe, structured estimates instead of unsafe or extreme prescriptions.

## Main features

- Premium landing page and onboarding flow
- Secure registration and login with hashed passwords
- Dashboard with user profile and saved plan history
- Goal-based plan generation for weight loss, muscle gain and strength gain
- Safety-aware rule-based AI fallback
- Validation, rate limiting and security headers
- Responsive dark interface for desktop and mobile

## Tech stack

- Python 3.12
- Flask 3.0
- SQLite
- Jinja2 templates
- Vanilla JavaScript frontend
- pytest for regression testing

## Project structure

- `backend/` — API routes, auth and database access
- `frontend/` — templates and static assets
- `ai/` — AI generation logic and fallback responses
- `config/` — environment and application settings
- `utils/` — validation and metric calculations
- `tests/` — regression tests

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
pip install pytest
```

3. Copy `.env.example` to `.env` and populate the values.
4. Run the app:

```bash
python main.py
```

Then open `http://127.0.0.1:5000/`.

## Environment variables

- `HOST`
- `PORT`
- `DEBUG`
- `APP_ENV`
- `SECRET_KEY`
- `SESSION_COOKIE_SECURE`
- `CORS_ALLOWED_ORIGINS`
- `AI_PROVIDER`
- `AI_API_URL`
- `AI_API_KEY`
- `AI_MODEL`
- `AI_TIMEOUT_SECONDS`
- `AI_FALLBACK_ENABLED`
- `RATE_LIMIT_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`

## Development and production notes

- Always keep `.env` out of version control.
- Use `DEBUG=false` in production.
- For deployment, run behind a WSGI server such as Gunicorn.
- Keep AI usage server-side and never expose API credentials to the front end.
- For minors, the app prioritizes safe habits, hydration, sleep, recovery and gradual progression rather than aggressive body-comparison or extreme dieting advice.

## Security notes

- Passwords are stored using Werkzeug hashes.
- API responses are validated before display.
- Authentication is session-based and route-protected.
- CORS and security headers are enabled for the configured origins.
- User data is kept in the local SQLite database and not exposed across accounts.

## Testing

```bash
python -m pytest -q
```
