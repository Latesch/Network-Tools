from app.services import logs_service


def test_save_and_get_log(app):
    """Создание и получение лога."""
    with app.app_context():
        logs_service.create_log(
            action="ping",
            host="8.8.8.8",
            params={"count": 4},
            status="ok",
            output="Success",
        )
        logs = logs_service.get_all_logs()
        assert len(logs) == 1
        assert logs[0].action == "ping"


def test_delete_log(app):
    """Удаление одного лога."""
    with app.app_context():
        logs_service.create_log("ping", "8.8.8.8", {}, "ok", "Success")
        logs = logs_service.get_all_logs()
        log_id = logs[0].id
        result = logs_service.delete_log(log_id)
        assert result is True
        assert len(logs_service.get_all_logs()) == 0


def test_delete_all_logs(app):
    """Удаление всех логов."""
    with app.app_context():
        for i in range(3):
            logs_service.create_log("ping", f"8.8.8.{i}", {}, "ok", "Success")
        logs_service.delete_all_logs()
        assert len(logs_service.get_all_logs()) == 0
