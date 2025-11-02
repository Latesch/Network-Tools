def test_login_page_loads(client):
    """Страница логина должна открываться."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "Войти" in response.text


def test_register_page_loads(client):
    """Страница регистрации должна открываться."""
    response = client.get("/register")
    assert response.status_code == 200
    assert "Регистрация" in response.text
