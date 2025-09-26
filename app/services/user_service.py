from typing import List

from werkzeug.security import check_password_hash, generate_password_hash

from app.interfaces.repositories import user_repo
from app.models.user import User


def register_user(
    username: str, password: str, confirm_password: str, role: str = "user"
) -> bool | None:
    """
    Регистрирует нового пользователя, если имя не занято и пароли совпадают.

    Args:
        username (str): Имя пользователя.
        password (str): Пароль.
        confirm_password (str): Подтверждение пароля.
        role (str): Роль пользователя (по умолчанию "user").

    Returns:
        bool: True если пользователь создан или False,
                        если имя занято или пароли не совпадают.
    """
    if user_repo.get_by_username(username):
        return False

    if password != confirm_password:
        return False

    password_hash = generate_password_hash(password, method="pbkdf2:sha256")
    user = User(username=username, password_hash=password_hash, role=role)
    user_repo.save(user)
    return True


def authenticate_user(username: str, password: str) -> User | None:
    """
    Проверяет логин и пароль пользователя.

    Args:
        username (str): Имя пользователя.
        password (str): Пароль.

    Returns:
        User | None: Пользователь при успешной аутентификации или None.
    """
    user = user_repo.get_by_username(username)
    if not user:
        return None
    if not check_password_hash(user.password_hash, password):
        return None
    return user


def get_all_users(current_user_role: str) -> List[User] | None:
    """
    Возвращает список всех пользователей,
    если текущий пользователь имеет доступ.

    Args:
        username (str): Имя пользователя.

    Returns:
        List[User] | None: Список пользователей,
        или None если роль текущего пользователя не админ.
    """
    if current_user_role != "admin":
        return None
    return user_repo.get_all()


def get_user_by_id(user_id: int) -> List[User]:
    """
    Возвращает пользователя по его ID.

    Args:
        user_id (int): ID пользователя.

    Returns:
        User | None: Пользователь, если найден,
                     иначе None.
    """
    return user_repo.get_by_id(user_id)


def delete_user(user_id: int, current_user_role: str) -> bool:
    """
    Удаляет пользователя по ID с проверкой прав доступа.

    Args:
        user_id (int): ID удаляемого пользователя.
        current_user_role (str): Роль текущего пользователя.

    Returns:
        bool: True, если пользователь успешно удалён.
              False, если нет прав, пользователь не найден,
              или это администратор.
    """
    if current_user_role != "admin":
        return False

    user = user_repo.get_by_id(user_id)
    if not user:
        return False

    if user.role == "admin":
        return False

    return user_repo.delete_by_id(user_id)
