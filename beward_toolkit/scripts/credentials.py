#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import PASSWORDS, PASSWORDS_BASE

from beward_cgi.toolkit import check_credentials

CREDENTIALS_FILTERS = {
    "Groups": [],
    "City": [],
}


def parse_credentials_filtres(filtres):
    """Парсинг фильтров

    Args:
        filtres (CREDENTIALS_FILTERS): переданные фильтры
    """
    groups = []
    for group in filtres.get("Groups", []):
        group = PASSWORDS["entries_groups"].get(group, "")
        if not group:
            continue
        groups.append(PASSWORDS_BASE.find_groups(name=group, first="True"))
    citys = [city for city in filtres.get("City", [])]
    return (groups, citys)


def found_credentials(ip, filter=None):
    """Поиск учетных данных на основе базы Keepass
    Args:
        ip(str): ip устройства
    """
    if filter is not None:
        groups, citys = parse_credentials_filtres(filter)
        entries = {}
        for group in groups:
            entries.update({group: []})
            for city in citys:
                entries[group] + PASSWORDS_BASE.find_entries(
                    group=group,
                    string={"City": city},
                )
        print(entries)
    credentials = {}
    [credentials.update({group: []}) for group in PASSWORDS["entries_groups"].values()]
    # gmc_group = PASSWORDS_BASE.find_groups(name=PASSWORDS["entries_groups"]["gmc"], first="True")
    # print(PASSWORDS_BASE.find_entries(group=gmc_group, string={"City": "Samara"}, first="True"))
    for group in PASSWORDS["entries_groups"].values():
        admin_credintials = PASSWORDS_BASE.find_groups(name=group, first="True").entries
        for entrie in admin_credintials:
            status = check_credentials(ip, entrie.username, entrie.password)
            # print((entrie.get_custom_property('City')))
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
