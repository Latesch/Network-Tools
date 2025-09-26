from typing import List

from app.infrastructure.extensions import db
from app.models.log import Log


def save(
    action: str,
    host: str,
    params: dict,
    status: str,
    output: str,
) -> None:
    """
    Сохраняет новый лог в базу данных.

    Args:
        action (str): Выполняемое действие (например, "ping").
        host (str): Хост, к которому выполнялась команда.
        params (dict): Параметры запроса.
        status (str): Статус выполнения ("ok", "warn" или "danger").
        output (str): Вывод команды.
    """
    log = Log(
        action=action,
        host=host,
        params=params,
        status=status,
        output=output,
    )
    db.session.add(log)
    db.session.commit()


def get_by_id(log_id: int) -> Log | None:
    """
    Возвращает лог по его ID.

    Args:
        log_id (int): Идентификатор лога.

    Returns:
        Log | None: Объект Log, если найден, иначе None.
    """
    return Log.query.get(log_id)


def delete_by_id(log_id: int) -> bool:
    """
    Удаляет лог по его ID.

    Args:
        log_id (int): Идентификатор лога.

    Returns:
        bool: True если удалён, False если не найден.
    """
    log = Log.query.get(log_id)
    if log:
        db.session.delete(log)
        db.session.commit()
        return True
    return False


def get_all() -> List[Log]:
    """
    Возвращает список всех действий.

    Returns:
        List[Log]: Список действий.
    """
    return Log.query.all()


def delete_all() -> None:
    """
    Удаляет все логи из базы данных.

    Returns:
        None
    """
    Log.query.delete()
    db.session.commit()
