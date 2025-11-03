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
    default_db_uri = f"sqlite:///{db_path}"

    if (
        os.getenv("TESTING") in ("1", "True", "true")
        or os.getenv("FLASK_ENV") == "testing"
    ):
        sql_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
    else:
        sql_uri = os.getenv("SQLALCHEMY_DATABASE_URI", default_db_uri)

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "fallback-secret"),
        "SQLALCHEMY_DATABASE_URI": sql_uri,
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        ).lower()
        in ("true", "1", "yes"),
        "MIGRATIONS_ENABLED": os.getenv("MIGRATIONS_ENABLED", "0") == "1",
        "APP_HOST": os.getenv("APP_HOST", "127.0.0.1"),
        "APP_PORT": int(os.getenv("APP_PORT", 5000)),
        "DEFAULT_DNS": os.getenv("DEFAULT_DNS", "8.8.8.8"),
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", None),
        "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", None),
    }
