from app.interfaces.repositories import user_repo
from app.services import user_service


def test_register_user_success(app):
    """Регистрация нового пользователя проходит успешно."""
    with app.app_context():
        result = user_service.register_user("late", "123", "123")
        assert result is True
        user = user_repo.get_by_username("late")
        assert user is not None


def test_register_user_password_mismatch(app):
    """Если пароли не совпадают — регистрация должна вернуть False."""
    with app.app_context():
        result = user_service.register_user("alex", "123", "321")
        assert result is False


def test_register_user_duplicate(app):
    """Повторная регистрация того же имени должна вернуть False."""
    with app.app_context():
        user_service.register_user("alex", "123", "123")
        result = user_service.register_user("alex", "456", "456")
        assert result is False


def test_authenticate_user_success(app):
    """Авторизация должна вернуть пользователя при корректных данных."""
    with app.app_context():
        user_service.register_user("john", "111", "111")
        user = user_service.authenticate_user("john", "111")
        assert user.username == "john"


def test_authenticate_user_wrong_password(app):
    """При неверном пароле — None."""
    with app.app_context():
        user_service.register_user("kate", "111", "111")
        user = user_service.authenticate_user("kate", "wrong")
        assert user is None
