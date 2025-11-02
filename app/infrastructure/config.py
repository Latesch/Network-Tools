import os

from dotenv import load_dotenv


def load_config():
    """
    Загружает конфигурацию из .flaskenv / .env файлов и переменных окружения.
    """
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv()

    instance_dir = os.path.join(base_dir, "..", "instance")
    os.makedirs(instance_dir, exist_ok=True)

    db_path = os.path.join(instance_dir, "nettools.db")
    db_uri = f"sqlite:///{db_path}"

    if os.getenv("FLASK_ENV") == "testing" or os.getenv("TESTING") == "1":
        db_uri = "sqlite:///:memory:"

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "fallback-secret"),
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "SQLALCHEMY_DATABASE_URI", db_uri
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        ).lower()
        in ("true", "1", "yes"),
        "MIGRATIONS_ENABLED": os.getenv("MIGRATIONS_ENABLED", "0") == "1",
    }
