from datetime import datetime

from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.extensions import db


class Log(db.Model):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=db.func.now(),
    )
    action: Mapped[str] = mapped_column(db.String(64), nullable=False)
    host: Mapped[str] = mapped_column(db.String(128), nullable=False)
    params: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(db.String(16), nullable=False)
    output: Mapped[str] = mapped_column(db.Text, nullable=False)
