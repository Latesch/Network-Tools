from flask import Flask
from .extensions import db, login_manager
from .view import bp
import os


def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static")
    )
    app.config["SECRET_KEY"] = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nettools.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(bp)

    return app


app = create_app()
