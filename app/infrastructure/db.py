from .extensions import db


def init_db(app):
    """
    Инициализирует базу данных и создаёт таблицы при первом запуске.
    """
    with app.app_context():
        db.create_all()
