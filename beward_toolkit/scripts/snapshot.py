#!/usr/bin/python3
# coding=utf8
from os import utime
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

from interface import HOST_PARSER, CREDENTIALS_PARSER
from interface import LIST_PARSER, STRING_PARSER, ZIP_PARSER
from interface import get_epiloge_message
from general_solutions import ping, run_command_to_seqens
from general_solutions import create_zip, get_gmc_id
from beward_cgi.general.client import BewardClient
from beward_cgi.images import ImagesModule
from beward_cgi.date import BewardTimeZone, DateModule
from beward_cgi.ntp import NtpModule
from beward_cgi.textoverlay import TextOverlayModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials


"""Модуль скриптов для создания скриншотов с панелей Beward"""


TIMEZONE_ABBREVIATION = [tz.get("abbreviation") for tz in BewardTimeZone._TIMEZONE]


def _get_date_from_datestring(datestring):
    """
    Получить дату из строки с датой

    Args:
        datestring (str): Исходная строка даты в формате
        'DD.MM.YYYY' или 'DD.MM.YYYY HH:MM'.

    Returns:
        datetime: Объект datetime, представляющий дату и время.

    Raises:
        ValueError: Если в строке нет ни времени, ни даты;
        входная строка не соответствует ожидаемому формату.

    Example:
        >>> date_str = '01.01.2022T12:30'
        >>> _get_date_from_datestring(date_str)
        datetime.datetime(2022, 1, 1, 12, 30, 38)
    """
    # паттерн для исходной строки с датой
    date_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    # паттерн для исходной строки с датой и временем
    datetime_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})T(\d{1,2}):(\d{1,2})"
    # ищем совпадения по каждому паттерну
    match_datestring = match(date_pattern, datestring)
    match_datetimestring = match(datetime_pattern, datestring)
    # проверяем наличие даты и времени в строке
    check_date_string = match_datestring is None
    check_datetime_string = match_datetimestring is None
    # генерируем случайное время, если не указано время в строке
    second = randint(0, 59)
    if all([check_date_string, check_datetime_string]):
        raise ValueError("Invalid datestring! Need format"
                         "'DD.MM.YYYY' or 'DD.MM.YYYY HH:MM'")
    if not check_datetime_string:
        day, month, year, hour, minute = match_datetimestring.groups()
        return (datetime(int(year), int(month), int(day),
                         int(hour), int(minute), int(second)), False)
    day, month, year = match_datestring.groups()
    # генерируем случайное время в стандартное рабочее время
    hour = randint(8, 18)
    minute = randint(0, 59)
    return (datetime(int(year), int(month), int(day),
                     int(hour), int(minute), int(second)), True)


def _get_snapshot_savepath(save_path=".", name=None, file_format="jpeg"):
    """
    Функция предназначена для получения пути файла сохранения скриншота.

    Args:
        save_path (строка): путь к директории для сохранения скриншотов.
        По умолчанию значение равно текущей директории.
        name (строка, необязательно): имя файла скриншота.
        Если name не указано, то функция будет генерировать
        уникальное имя для файла скриншота.
        file_format (строка): формат файла скриншота. По умолчанию - jpeg.

    Returns:
        Path: объект класса Path, представляющий путь для сохранения скриншота.
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
    """
    Получение скриншота с панели

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        channel (str): Номер канала. По умолчанию "0".
        save (bool): Сохранять полученный снимок на жесткий диск. По умолчанию True.
        file_format (str): Формат файла снимка. По умолчанию "jpeg".
        save_path (str): Директория для сохранения снимка. По умолчанию текущая директория <.>
        snapshot_name (str): Имя файла снимка. По умолчанию текущее время.
        changed_date (tuple): Дата и часовой пояс для установки на панель.
        Требуется передать кортеж из двух элементов: (datetime, str)
        где datetime - дата и время в формате datetime.datetime,
        str - часовой пояс в формате аббревиатуры ("ALMT", "EET" и т.д.).
        По умолчанию пустой кортеж.

    Returns:
        Если save=True, возвращает директорию при успешном сохранении файла снимка.
        Если save=False, возвращает кортеж из двух элементов:
        (имя файла, двоичный объект снимка) при успешном получении снимка.

    Raises:
        ValueError: Если не указан ip адрес панели
        ValueError: Если измененная дата передана с некорректными аргументами
        ValueError: Если измененный часовой пояс не из списка TIMEZONE_ABBREVIATION
        ValueError: Если передан кортеж с некорректными элементами

    """
    # Валидация аргументов
    if ip is None:
        raise ValueError("IP not specified")
    if changed_date:
        if len(changed_date) != 2:
            raise ValueError("Changed date must be 2 elements."
                             "(date(datetime), tz_abbreviation(str))")
        date, tz_abbreviation = changed_date
        date = date[0]
        if not isinstance(date, datetime):
            raise ValueError("Changed date must be datetime.datetime")
        if not isinstance(tz_abbreviation, str):
            raise ValueError("Changed date must be str")
        if tz_abbreviation not in TIMEZONE_ABBREVIATION:
            raise ValueError("Changed date must be one of %s" % TIMEZONE_ABBREVIATION)
    # Подбор аргументов
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    # Переменные
    name_format = "{name}.{file_format}"
    client = BewardClient(ip=ip, login=username, password=password)
    image_client = ImagesModule(client=client)
    ntp_client = NtpModule(client=client)
    date_client = DateModule(client=client)
    textoverlay_client = TextOverlayModule(client=client)

    if snapshot_name is None or snapshot_name == "":
        # Пробуем вытащить индификатор из названия RTSP
        textoverlay_client.load_params()
        title = textoverlay_client.get_params().get("Title", "")
        snapshot_name = get_gmc_id(title=title)

        if not snapshot_name:
            snapshot_name = int(time())

    name = name_format.format(name=snapshot_name, file_format=file_format)
    # Изменение даты на панели
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
    # Получение снимка
    binary_image = image_client.get_images(channel, False)
    # Возвращаем параметры NTP
    if changed_date:
        ntp_client.set_params()
    # Сохранение снимка
    if save:
        save_path = _get_snapshot_savepath(save_path, name, file_format)
        with open(save_path, 'wb') as snapshot_file:
            snapshot_file.write(binary_image)
        if changed_date:
            timestamp = int(date.timestamp())
            utime(save_path, times=(timestamp, timestamp))
        return save_path
    # Возвращаем кортеж из двух элементов: (имя файла, двоичный объект снимка)
    return (name, binary_image)


def get_snapshot_hosts(hosts=None, username=None, password=None, thread_num=1,
                       channel="0", file_format="jpeg", save_path=".",
                       changed_date=(), archiveted=False):
    """
    Получает снимки с камер по списку хостов.

    Args:
        hosts (Список[str/dict]): Список хостов, на которых требуется получить снимок.
        username (str): Имя пользователя, используемое для аутентификации на хостах.
        password (str): Пароль для аутентификации на хостах.
        thread_num (int): Количество потоков, используемых для выполнения команд.
        channel: (str): Номер канала для получения снимка.
        file_format (str): Формат файла для сохранения снимка.
        save_path (str): Путь для сохранения снимков.
        changed_date (tuple): Диапазон даты изменения файлов.
        archiveted(bool) архивировать ли скриншоты.

    Returns:
        Нет возвращаемых значений. Но создаются файлы в переданной деректории.

    """
    output = []
    seqens = []
    if hosts is None or not hosts:
        raise ValueError("Hosts not specified")

    for item in hosts:
        if isinstance(item, dict):
            host = item.get("IP", "")
            name = item.get("Name", "")
        elif isinstance(host, str):
            name = ''
            host = item
        else:
            ValueError("Host must be str or dict")

        if not ping(host):
            continue

        if changed_date is not None or not changed_date:
            if changed_date[0][1]:
                # Если время в дате сгенерировано рандоимно, оно генерируеться повторно
                date = datetime.strftime(changed_date[0][0], "%d.%m.%Y")
                date = _get_date_from_datestring(date)
                changed_date = tuple([date, changed_date[1]])

        host_seqens = (host, username, password, channel,
                       file_format, save_path, changed_date, name)
        seqens.append(host_seqens)
    output += run_command_to_seqens(
        get_snapshot,
        seqens,
        ("ip", "username", "password", "channel", "file_format",
         "save_path", "changed_date", "snapshot_name"),
        thread_num,
    )
    if archiveted:
        archive_name = "snapshot-archive-{}".format(int(time()))
        path_collection = [_[1] for _ in output if _ is not None or len(_) > 1]
        _, path_to_archive = create_zip(name=archive_name, zip_path=save_path,
                                        files_path_collection=path_collection,
                                        remove_files=True)
        return path_to_archive
    return output


def parse_args():
    """Настройка argparse"""
    epilog_message = get_epiloge_message("1.0", "Nikita Vasilev (catemohi@gmail.com)",
                                         "06.04.2023")
    general_parser = ArgumentParser(add_help=False)
    general_parser.add_argument("-c", "--channel", metavar="X", default="0",
                                help="канал RTSP потока. По умолчанию 0")
    general_parser.add_argument("--path", metavar="./.", default=".",
                                help=("путь к дериктории сохранения "
                                      "скриншота. По умолчанию <.>"))
    general_parser.add_argument("--format", metavar="xxx", default="jpeg",
                                help=("формат сохранения скриншотов."
                                      "По умолчанию <jpeg>"))
    general_parser.add_argument("-d", "--date",
                                metavar="<DD.MM.YYYY> | <DD.MM.YYYYThh:mm>",
                                default=None, type=_get_date_from_datestring,
                                help=("Дата, если требуется "
                                      "поменять дату на скриншоте. "
                                      "Форматы даты <DD.MM.YYYY>; <DD.MM.YYYY HH:MM>"))
    general_parser.add_argument("-t", "--timezone", metavar="XXX",
                                default="MSK", choices=TIMEZONE_ABBREVIATION,
                                help="Аббревиатура временой зоны.\n{}"\
                                        .format(';'.join(TIMEZONE_ABBREVIATION)))

    parser = ArgumentParser(prog='snapshot', description=("Создание скриншотов "
                                                          "с панелей Beward"),
                            epilog=epilog_message, formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers()
    parser_host = subparsers.add_parser('host', help='запуск скрипта для одного адреса',
                                        parents=[CREDENTIALS_PARSER, HOST_PARSER,
                                                 general_parser],
                                        formatter_class=RawTextHelpFormatter)
    parser_host.add_argument("-n", "--name", metavar="xxx",
                             default=None, help="имя скриншота")
    parser_host.set_defaults(func="host")

    parser_list = subparsers.add_parser('list', help=("запуск скрипта для списка"
                                                      " адресов из csv файла."),
                                        parents=[CREDENTIALS_PARSER,
                                                 LIST_PARSER, general_parser,
                                                 ZIP_PARSER],
                                        formatter_class=RawTextHelpFormatter)
    parser_list.set_defaults(func="list")

    parser_string = subparsers.add_parser('string',
                                          help=("запуск скрипта для списка"
                                                "адресов из текстовой линии."),
                                          parents=[CREDENTIALS_PARSER,
                                                   STRING_PARSER,
                                                   general_parser, ZIP_PARSER],
                                          formatter_class=RawTextHelpFormatter)
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
    elif args.func == "list":
        try:
            get_snapshot_hosts(
                hosts=args.csvpath,
                username=args.username,
                password=args.password,
                channel=args.channel,
                thread_num=args.thread,
                file_format=args.format,
                save_path=args.path,
                changed_date=args.date,
                archiveted=args.archiveted,
            )
        except Exception as e:
            print(str(e))
    elif args.func == "string":
        try:
            get_snapshot_hosts(
                hosts=args.string,
                username=args.username,
                password=args.password,
                channel=args.channel,
                thread_num=args.thread,
                file_format=args.format,
                save_path=args.path,
                changed_date=args.date,
                archiveted=args.archiveted,
            )
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    main()
