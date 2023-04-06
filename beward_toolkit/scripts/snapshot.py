#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path
from random import randint
from time import time
from datetime import datetime
from re import match
from argparse import ArgumentParser, RawTextHelpFormatter

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from interface import HOST_PARSER, CREDENTIALS_PARSER, LIST_PARSER, STRING_PARSER
from interface import get_epiloge_message
from general_solutions import get_reachable_hosts, ping, run_command_to_seqens, get_terminal_size
from beward_cgi.general.client import BewardClient
from beward_cgi.images import ImagesModule
from beward_cgi.date import BewardTimeZone, DateModule
from beward_cgi.ntp import NtpModule
# from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials



"""Модуль скриптов для создания скриншотов с панелей Beward"""


TIMEZONE_ABBREVIATION = [tz.get("abbreviation") for tz in BewardTimeZone._TIMEZONE]


def _get_date_from_datestring(datestring):
    """Получить дату из строки с датой

    Args:
        datestring (str): исходная строка даты
    """
    date_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    datetime_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})T(\d{1,2}):(\d{1,2})"
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
    # Change time to Beward panel
    if changed_date:
        date_client.load_params()
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
    binary_image = image_client.get_images(channel, False)
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
    epilog_message = get_epiloge_message("1.0", "Nikita Vasilev (catemohi@gmail.com)", "06.04.2023")
    general_parser = ArgumentParser(add_help=False)
    general_parser.add_argument("-c", "--channel", metavar="X", default="0", help="канал RTSP потока. По умолчанию 0")
    general_parser.add_argument("--path", metavar="/.", default=".", help="путь к дериктории сохранения скриншота. По умолчанию <.>")
    general_parser.add_argument("--format", metavar="xxx", default="jpeg", help="формат сохранения скриншотов. По умолчанию <jpeg>")
    general_parser.add_argument("-n", "--name", metavar="xxx", default=None, help="имя скриншота")
    general_parser.add_argument("-d", "--date", metavar="<DD.MM.YYYY> | <DD.MM.YYYYThh:mm>",
                                default=None,
                                type=_get_date_from_datestring,
                                help="Дата, если требуеться поменять дату на скриншоте. Форматы даты <DD.MM.YYYY>; <DD.MM.YYYY HH:MM>")
    general_parser.add_argument("-t", "--timezone", metavar="XXX", default="MSK", choices=TIMEZONE_ABBREVIATION, help="Аббревиатура временой зоны.\n{}".format(';'.join(TIMEZONE_ABBREVIATION)))

    parser = ArgumentParser(prog='snapshot', description='Создание скриншотов с панелей Beward',
                            epilog=epilog_message, formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers()
    parser_host = subparsers.add_parser('host', help='запуск скрипта для одного адреса',
                                        parents=[CREDENTIALS_PARSER, HOST_PARSER, general_parser], formatter_class=RawTextHelpFormatter)
    parser_host.set_defaults(func="host")

    parser_list = subparsers.add_parser('list', help='запуск скрипта для списка адресов из csv файла.',
                                        parents=[CREDENTIALS_PARSER, LIST_PARSER, general_parser], formatter_class=RawTextHelpFormatter)
    parser_list.set_defaults(func="list")

    parser_string = subparsers.add_parser('string', help='запуск скрипта для списка адресов из текстовой линии.',
                                          parents=[CREDENTIALS_PARSER, STRING_PARSER, general_parser], formatter_class=RawTextHelpFormatter)
    parser_string.set_defaults(func="string")

    return parser.parse_args()


def main():
    """Это все, что нам потребуется для обработки всех ветвей аргументов"""
    args = parse_args()
    if args.date is not None:
        args.date = (args.date, args.timezone)
    if args.func == "host":
        try:
            get_snapshot(
                ip=args.ip,
                username=args.username,
                password=args.password,
                channel=args.channel,
                save=True,
                file_format=args.format,
                save_path=args.path,
                snapshot_name=args.name,
                changed_date=args.date,
            )
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    main()
