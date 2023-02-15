from .general.client import Client

"""Полезные скрипты для взаимодествия с панелями
"""


def check_credentials(ip=None, username=None, password=None):
    """Проверяет наличие учетной записи в локальной базе данных панели.

    Args:
        ip (str, optional): ip адрес панели. Defaults to None.
        username (str, optional): имя пользователя. Defaults to None.
        password (str, optional): пароль пользователя. Defaults to None.
    """
    client = Client(ip=ip, username=username, password=password)
    status = client.check_credentials()
    client.close()
    return status
