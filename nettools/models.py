from .extensions import db
from sqlalchemy.dialects.sqlite import JSON
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, method="pbkdf2:sha256"
        )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    action = db.Column(db.String(64))
    host = db.Column(db.String(128))
    params = db.Column(JSON)
    status = db.Column(db.String(16))
    output = db.Column(db.Text)

    @classmethod
    def save(cls, action, host, params, status, output):
        log = cls(
            action=action,
            host=host,
            params=params,
            status=status,
            output=output
        )
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def delete_by_id(cls, log_id):
        log = cls.query.get(log_id)
        if log:
            db.session.delete(log)
            db.session.commit()
            return True
        return False

    @classmethod
    def clear_all(cls):
        cls.query.delete()
        db.session.commit()

    def __repr__(self):
        return f"<Log {self.id} {self.action} {self.host}>"
