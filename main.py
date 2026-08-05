from backend.app import app
from config.settings import Settings


if __name__ == "__main__":
    settings = Settings()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
