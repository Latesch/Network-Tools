from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=db.func.now(),
    )
    username: Mapped[str] = mapped_column(
        db.String(64),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(db.String(128), nullable=False)
    role: Mapped[str] = mapped_column(db.String(20), default="user")
