#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import PASSWORDS, PASSWORDS_BASE

from beward_cgi.toolkit import check_credentials


def found_credentials(ip):
    """Поиск учетных данных на основе базы Keepass
    Args:
        ip(str): ip устройства
    """
    credentials = {}
    [credentials.update({group: []}) for group in PASSWORDS["entries_groups"].values()]
    for group in PASSWORDS["entries_groups"].values():
        admin_credintials = PASSWORDS_BASE.find_groups(name=group, first="True").entries
        for entrie in admin_credintials:
            status = check_credentials(ip, entrie.username, entrie.password)
            if status:
                credentials[group].append((entrie.username, entrie.password))
    return credentials


def check_or_brut_admin_credentials(ip, username, password):
    """Функция проверки учетных данных или попытки подбора на основе базы

    Args:
        ip (str): IP устройства
        username (str, optional): Имя пользователя. Defaults to None.
        password (str, optional): Пароль пользователя. Defaults to None.

    Raises:
        ValueError: Не удалось подобрать учетные данные.
        ValueError: Учетные данные не корректны.

    Returns:
        tuple: username, password
    """
    if username is None or password is None:
        credentials = found_credentials(ip)
        if not credentials[PASSWORDS["entries_groups"]["admin"]]:
            raise ValueError("Admin credentials, not found")
        return credentials[PASSWORDS["entries_groups"]["admin"]][0]
    if check_credentials(ip, username, password):
        return (username, password)
    raise ValueError("Credentials incorrect")


if __name__ == "__main__":
    print(found_credentials("10.80.1.200"))