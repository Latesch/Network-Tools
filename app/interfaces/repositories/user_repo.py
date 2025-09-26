from typing import List

from app.infrastructure.extensions import db
from app.models.user import User


def get_by_username(username: str) -> User | None:
    """
    Возвращает пользователя по имени.

    Args:
        username (str): Имя пользователя.

    Returns:
        User | None: Пользователь, если найден, иначе None.
    """
    return User.query.filter_by(username=username).first()


def get_by_id(user_id: int) -> User | None:
    """
    Возвращает пользователя по ID.

    Args:
        user_id (int): ID пользователя.

    Returns:
        User | None: Пользователь, если найден, иначе None.
    """
    return User.query.get(user_id)


def get_role(user_id: int) -> str | None:
    """
    Возвращает роль пользователя по его ID.

    Args:
        user_id (int): ID пользователя.

    Returns:
        str: Роль пользователя текстом, по умолчанию user.
        None: Если не нашел пользователя по user_id.
    """
    user = User.query.get(user_id)
    return user.role if user else None


def get_all() -> List[User]:
    """
    Возвращает список всех пользователей.

    Returns:
        List[User]: Список пользователей.
    """
    return User.query.all()


def save(user: User) -> None:
    """
    Сохраняет пользователя в базу данных.

    Args:
        user (User): Объект пользователя.
    """
    db.session.add(user)
    db.session.commit()


def delete_by_id(user_id: int) -> bool:
    """
    Удаляет пользователя по его ID.

    Args:
        user_id (int): ID пользователя.

    Returns:
        bool: True если удалён, False если не найден.
    """
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False


def delete_all() -> None:
    """
    Удаляет всех пользователей из базы данных.

    Returns:
        None
    """
    User.query.delete()
    db.session.commit()
