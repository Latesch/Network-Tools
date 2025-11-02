import os

from dotenv import load_dotenv


def load_config():
    """
    Загружает конфигурацию из .flaskenv / .env файлов и переменных окружения.
    """
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv()

    db_path = os.path.join(BASE_DIR, "..", "instance", "nettools.db")
    db_uri = f"sqlite:///{db_path}"

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "fallback-secret"),
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "SQLALCHEMY_DATABASE_URI", db_uri
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )
        == "True",
        "MIGRATIONS_ENABLED": os.getenv("MIGRATIONS_ENABLED", "0") == "1",
    }
