def test_index_page_loads(client):
    """Главная страница должна быть доступна."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Ping" in response.text or "Traceroute" in response.text


def test_connect_page_loads(client):
    """Страница подключения должна открываться."""
    response = client.get("/connect")
    assert response.status_code == 200
