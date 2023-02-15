#!/usr/bin/python
# coding=utf8
from .general.client import Client

"""Полезные скрипты для взаимодествия с панелями
"""


def check_credentials(ip=None, login=None, password=None):
    """Проверяет наличие учетной записи в локальной базе данных панели.

    Args:
        ip (str, optional): ip адрес панели. Defaults to None.
        login (str, optional): имя пользователя. Defaults to None.
        password (str, optional): пароль пользователя. Defaults to None.
    """
    if all[ip is not None, login is not None, password is not None]:
        raise ValueError("Invalid credentials")
    client = Client(ip=ip, login=login, password=password)
    status = client.check_credentials()
    client.close()
    return status
