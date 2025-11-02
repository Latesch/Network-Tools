from app.services.nettools_service import valid_ip


def test_valid_ip_correct_ipv4():
    """Корректный IPv4 должен пройти валидацию."""
    assert valid_ip("192.168.1.1") is True


def test_valid_ip_invalid_ipv4():
    """Некорректный IPv4 должен быть отклонён."""
    assert valid_ip("192.168.1.999") is False


def test_valid_ip_correct_ipv6():
    """Корректный IPv6 должен пройти валидацию."""
    assert valid_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True


def test_valid_ip_invalid_ipv6():
    """Некорректный IPv6 должен быть отклонён."""
    assert valid_ip("2001:db8:85g3::8a2e:370:7334") is False


def test_valid_hostname():
    """Корректное доменное имя."""
    assert valid_ip("example.com") is True


def test_valid_hostname_with_invalid_chars():
    """Недопустимые символы в имени узла."""
    assert valid_ip("exa$mple!.com") is False
