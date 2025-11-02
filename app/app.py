import os

from flask import Flask

from app.infrastructure.config import load_config
from app.infrastructure.db import init_db
from app.infrastructure.extensions import db, login_manager, migrate
from app.interfaces.controllers.main_controller import bp


def create_app():
    """
    Фабрика Flask-приложения.
    Загружает конфигурацию, инициализирует расширения, регистрирует blueprints.
    """
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
        instance_relative_config=True,
    )

    config = load_config()
    app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)

    if app.config.get("MIGRATIONS_ENABLED"):
        migrate.init_app(app, db)
    else:
        init_db(app)

    app.register_blueprint(bp)

    return app


app = create_app()
