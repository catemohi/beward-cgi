#!/usr/bin/python
# coding=utf8
from argparse import ArgumentParser
from pathlib import Path
from sys import path
from random import randint
from time import time
from datetime import datetime
from re import match

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import get_reachable_hosts, ping, run_command_to_seqens

from beward_cgi.general.client import BewardClient
from beward_cgi.images import ImagesModule
from beward_cgi.date import BewardTimeZone, DateModule
from beward_cgi.ntp import NtpModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов для создания скриншотов с панелей Beward"""


TIMEZONE_ABBREVIATION = [tz.get("abbreviation") for tz in BewardTimeZone._TIMEZONE]


def _get_date_from_datestring(datestring):
    """Получить дату из строки с датой

    Args:
        datestring (str): исходная строка даты
    """
    date_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    datetime_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})\s(\d{1,2}):(\d{1,2})"
    match_datestring = match(date_pattern, datestring)
    match_datetimestring = match(datetime_pattern, datestring)
    check_date_string = match_datestring is None
    check_datetime_string = match_datetimestring is None
    second = randint(0, 59)
    if all([check_date_string, check_datetime_string]):
        raise ValueError("Invalid datestring! Need format 'DD.MM.YYYY' or 'DD.MM.YYYY HH:MM'")
    if not check_datetime_string:
        day, month, year, hour, minute = match_datetimestring.groups()
        return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
    day, month, year = match_datestring.groups()
    # inputs the random time of the standard working day
    hour = randint(8, 18)
    minute = randint(0, 59)
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))


def _get_snapshot_savepath(save_path=".", name=None, file_format="jpeg"):
    """Получить путь сохранения скриншота

    Args:
        name (str, optional): имя скриншота. Defaults to None.
    """
    save_path = Path(save_path)
    if name is None:
        name = int(time())
        name_format = "{name}.{file_format}"
        name = name_format.format(name=name, file_format=file_format)
    save_path = save_path / name
    return save_path.resolve()


def get_snapshot(
    ip=None,
    username=None,
    password=None,
    channel="0",
    save=True,
    file_format="jpeg",
    save_path=".",
    snapshot_name=None,
    changed_date=(),
):
    """Получение скриншота с панели
    Args:
        ip(str): IP адрес. По умолчанию None.
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    print("Get snapshot %s" % ip)
    # Validate
    if ip is None:
        raise ValueError("IP not specified")
    if changed_date:
        if len(changed_date) != 2:
            raise ValueError("Changed date must be 2 elements. (date(datetime), tz_abbreviation(str))")
        date, tz_abbreviation = changed_date
        if not isinstance(date, datetime):
            raise ValueError("Changed date must be datetime.datetime")
        if not isinstance(tz_abbreviation, str):
            raise ValueError("Changed date must be str")
        if tz_abbreviation not in TIMEZONE_ABBREVIATION:
            raise ValueError("Changed date must be one of %s" % TIMEZONE_ABBREVIATION)
    # Brut
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    # Variable
    if snapshot_name is None:
        snapshot_name = int(time())

    name_format = "{name}.{file_format}"
    name = name_format.format(name=snapshot_name, file_format=file_format)
    client = BewardClient(ip=ip, login=username, password=password)
    image_client = ImagesModule(client=client)
    ntp_client = NtpModule(client=client)
    date_client = DateModule(client=client)
    # Load parameters from Beward panel
    for module in (ntp_client, image_client):
        module.load_params()
    # Change time to Beward panel
    if changed_date:
        ntp_client.load_params()
        tz = BewardTimeZone(21)
        tz.set(abbreviation=tz_abbreviation)
        date_module = {
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "hour": date.hour,
            "minute": date.minute,
            "second": date.second,
            "timezone": tz,
        }
        date_client.update_params(update=date_module)
        date_client.set_params()
    # Get snapshots
    binary_image = client.get_images(channel, False)
    # Return NTP settings
    if changed_date:
        ntp_client.set_params()
    # Save snapshot
    if save:
        save_path = _get_snapshot_savepath(save_path, name, file_format)
        with open(save_path, 'wb') as snapshot_file:
            snapshot_file.write(binary_image)
        return True
    # Return raw snapshot
    return (name, binary_image)


def _validate_csvfile(csv_file):
    """_summary_

    Args:
        csv_file (_type_): _description_
    """
    ...


def parse_args():
    """Настройка argparse"""

    parser = ArgumentParser(description='Создание скриншотов с панелей Beward')
    subparsers = parser.add_subparsers()
    parser_host = subparsers.add_parser('host', help='Запуск скрипта для одного адреса')
    parser_host.add_argument("ip", help="IP адрес панели Beward")
    parser_host.add_argument("-u", "--username", default=None, help="Имя пользователя зарегистрированного на панели Beward")
    parser_host.add_argument("-p", "--password", default=None, help="Пароль пользователя зарегистрированного на панели Beward")
    parser_host.add_argument("-c", "--channel", default="0", help="Канал RTSP потока. По умолчанию 0")
    parser_host.add_argument("--path", default=".", help="Путь к дериктории сохранения скриншота. По умолчанию <.>")
    parser_host.add_argument("--format", default="jpeg", help="Формат сохранения скриншотов. По умолчанию <jpeg>")
    parser_host.add_argument("-n", "--name", default=None, help="Имя скриншота")
    parser_host.add_argument("-d", "--date", default=None, help="Дата, если требуеться поменять дату на скриншоте. Форматы даты <DD.MM.YYYY>; <DD.MM.YYYY HH:MM>")
    parser_host.add_argument("-t", "--timezone", default="MSK", help="Аббревиатура временой зоны. Допустимые аббриветуры: %s" % "; ".join(TIMEZONE_ABBREVIATION))
    parser_host.set_defaults(func=get_snapshot)

    parser_list = subparsers.add_parser('list', help='Запуск скрипта для списка адресов из csv файла.')
    parser_list.add_argument("csvpath", help="Путь к csv файлу. Требования в csv файле. Столбцы: IP, Name; Делиметр: <;>. Кодировка: UTF-8")
    parser_list.add_argument("-u", "--username", default=None, help="Имя пользователя зарегистрированного на панели Beward")
    parser_list.add_argument("-p", "--password", default=None, help="Пароль пользователя зарегистрированного на панели Beward")
    parser_list.add_argument("-c", "--channel", default="0", help="Канал RTSP потока. По умолчанию 0")
    parser_list.add_argument("--path", default=".", help="Путь к дериктории сохранения скриншота. По умолчанию <.>")
    parser_list.add_argument("--format", default="jpeg", help="Формат сохранения скриншотов. По умолчанию <jpeg>")
    parser_list.add_argument("-n", "--name", default=None, help="Имя скриншота")
    parser_list.add_argument("-d", "--date", default=None, help="Дата, если требуеться поменять дату на скриншоте. Форматы даты <DD.MM.YYYY>; <DD.MM.YYYY HH:MM>")
    parser_list.add_argument("-t", "--timezone", default="MSK", help="Аббревиатура временой зоны. Допустимые аббриветуры: %s" % "; ".join(TIMEZONE_ABBREVIATION))
    parser_list.set_defaults(func=get_snapshot)

    return parser.parse_args()


def main():
    """Это все, что нам потребуется для обработки всех ветвей аргументов"""
    args = parse_args()
    print(args)
    try:
        args.func(args)

    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
