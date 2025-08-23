from flask import Flask
from extensions import db, login_manager
from view import bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nettools.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # импортируем модели только после инициализации db
    from models import User, Log  
    with app.app_context():
        db.create_all()

    app.register_blueprint(bp)

    return app
