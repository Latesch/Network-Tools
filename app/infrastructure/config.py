import os

from dotenv import load_dotenv


def load_config():
    """
    Загружает конфигурацию из .flaskenv / .env файлов и переменных окружения.
    """
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    load_dotenv()

    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "fallback-secret"),
        "SQLALCHEMY_DATABASE_URI": os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            f"sqlite:///{os.path.join(BASE_DIR, '..', 'instance', 'nettools.db')}",
        ),
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv(
            "SQLALCHEMY_TRACK_MODIFICATIONS", "False"
        )
        == "True",
    }
