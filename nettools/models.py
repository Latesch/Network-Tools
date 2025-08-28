from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime, default=db.func.now(),
    )
    username: Mapped[str] = mapped_column(
        db.String(64), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    role: Mapped[str] = mapped_column(db.String(20), default="user")

    @classmethod
    def delete_user(cls, id: int) -> bool:
        user = cls.query.get(id)
        if user:
            if user.role == "admin":
                return False
            db.session.delete(user)
            db.session.commit()
            return True
        return False

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

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime, default=db.func.now(),
    )
    action: Mapped[str] = mapped_column(db.String(64), nullable=False)
    host: Mapped[str] = mapped_column(db.String(128), nullable=False)
    params: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(db.String(16), nullable=False)
    output: Mapped[str] = mapped_column(db.Text, nullable=False)

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
