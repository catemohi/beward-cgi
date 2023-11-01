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
    for group in filtres.get("Groups", PASSWORDS["entries_groups"].values()):
        if group not in PASSWORDS["entries_groups"].values():
            continue
        groups.append(PASSWORDS_BASE.find_groups(name=group, first="True"))
    # Добовляем "All", потому что если City == "All", значит он подходит
    # к любому городу
    citys = [city for city in filtres.get("City", [])] + ["All"]
    return (groups, citys)


def found_credentials(ip, filter=None):
    """Поиск учетных данных на основе базы Keepass
    Args:
        ip(str): ip устройства
    """
    entries = {}
    if filter is not None:
        groups, citys = parse_credentials_filtres(filter)
        for group in groups:
            entries.update({group.name: []})
            for city in citys:
                entries[group.name] += PASSWORDS_BASE.find_entries(
                    group=group,
                    string={"City": city},
                )

    else:
        for group in PASSWORDS["entries_groups"].values():
            entries.update(
                {group: PASSWORDS_BASE.find_groups(name=group, first="True").entries},
            )
    credentials = {}
    for group, entries_collection in entries.items():
        credentials[group] = []
        for entrie in entries_collection:
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
    print(
        found_credentials(
            "10.80.208.183",
            {
                "City": ["Samara", "Saint-Petersburg"],
                "Groups": [PASSWORDS["entries_groups"]["gmc"]],
            },
        ),
    )
