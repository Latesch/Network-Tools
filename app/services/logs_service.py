from typing import List, Optional

from app.interfaces.repositories import logs_repo
from app.models.log import Log


def get_all_logs() -> List[Log]:
    """
    Возвращает список всех логов.

    Returns:
        List[Log]: Список объектов Log.
    """
    return logs_repo.get_all()


def get_log_by_id(log_id: int) -> Optional[Log]:
    """
    Возвращает лог по ID.

    Args:
        log_id (int): Идентификатор лога.

    Returns:
        Log | None: Объект Log, если найден, иначе None.
    """
    return logs_repo.get_by_id(log_id)


def delete_log(log_id: int) -> bool:
    """
    Удаляет лог по его ID.

    Args:
        log_id (int): Идентификатор лога.

    Returns:
        bool: True, если удаление успешно.
              False, если лог не найден.
    """
    return logs_repo.delete_by_id(log_id)


def delete_all_logs() -> None:
    """
    Удаляет все логи из базы данных.
    """
    logs_repo.delete_all()


def export_logs_to_json() -> List[dict]:
    """
    Экспортирует все логи в список словарей (для JSON).

    Returns:
        List[dict]: Логи в формате словарей.
    """
    logs = logs_repo.get_all()
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "action": log.action,
            "host": log.host,
            "params": log.params,
            "status": log.status,
            "output": log.output,
        }
        for log in logs
    ]


def create_log(
    action: str,
    host: str,
    params: dict,
    status: str,
    output: str,
) -> None:
    """
    Создаёт новую запись в логах.

    Args:
        action (str): Действие (ping, traceroute, ssh, telnet и т.д.).
        host (str): Целевой хост.
        params (dict): Параметры запроса (без пароля!).
        status (str): Статус выполнения ("ok", "warn", "danger").
        output (str): Вывод команды.
    """

    logs_repo.save(
        action=action,
        host=host,
        params=params,
        status=status,
        output=output,
    )
