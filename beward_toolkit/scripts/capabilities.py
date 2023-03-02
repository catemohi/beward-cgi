#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from beward_cgi.user_capabilities import UserCapabilitiesModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов с правами пользователя на панели"""


def get_capabilites(ip, username=None, password=None):
    """Получение прав пользователей
    Args:
        ip(str): IP адрес
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    print(username, password)
    client = UserCapabilitiesModule(ip, username, password)
    client.load_params()
    print(client.get_params())


if __name__ == "__main__":
    get_capabilites("10.80.1.200")
