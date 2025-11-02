import os
import sys

import pytest

from app.app import create_app
from app.infrastructure.extensions import db

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture()
def app():
    """Создаёт временное Flask-приложение и чистую БД для каждого теста."""
    os.environ["TESTING"] = "1"
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        LOGIN_DISABLED=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Тестовый HTTP-клиент Flask."""
    return app.test_client()
