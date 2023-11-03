#!/usr/bin/python3
# coding=utf8
import argparse
from os.path import isfile
from re import match
from pathlib import Path
from sys import path
from json import load, dump

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from beward_cgi.rfid import RfidModule
from beward_cgi.mifare import MifareModule
from beward_cgi.general.client import BewardClient
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials
from beward_cgi.general.module import BewardIntercomModuleError
from interface import get_epiloge_message


###########################################################################
# TODO Добавить функцию 
## 1. кидаешь путь к zip архиву
## 2. скрипт расскрывает zip
## 3. считывает файлы, название файлов == ip
###########################################################################
# TODO Добавить default_parsers из модуля interface по аналогии со snapshot
###########################################################################
# TODO Добавить три режима работы с данными, как в snapshot
###########################################################################


"""
Модуль для взаимодействия с панелью через ключи RFID и MIFARE.

Этот модуль предоставляет функции, которые обеспечивают взаимодействие с панелью
с использованием ключей RFID или MIFARE. Он позволяет загружать и выгружать ключи,
а также создавать модуль для работы с ключами в зависимости от типа панели.

Функции:
- format_keysfile_to_keystring_array: Конвертирует данные из файла с ключами EQM в массив ключей.
- create_key_module_based_on_panel_type: Создает модуль для работы с ключами на основе типа панели.
- upload_keys_from_eqm_file: Загружает ключи на панель из файла формата EQM.
- dump_keys_to_json: Сохраняет ключи с панели в формате JSON.
- load_keys_from_json: Загружает ключи на панель из JSON файла.
"""

def format_keysfile_to_keystring_array(filepath):
    """
    Функция конвертирования данных из файла с ключами из EQM
    в массив с ключами.

    Args:
        filepath (str): Путь к файлу
    
    Raises:
        ValueError: Если в файла не существует;

    Returns:
        tuple: Массив с ключами и формат (тип) ключей

    Example:
        >>> file = \"\"\"
        [KEYS]
        KeyValue1=000000C2137B42
        KeyApartment1=0
        KeyIndex1=0
        KeyValue2=000000C21252E2
        KeyApartment2=0
        KeyIndex2=1
        \"\"\"
        >>> format_keysfile_to_keystring_array(to_file_path)
        (("000000C2137B42,0", "000000C21252E2,0"), "RFID")
        
        # Параметр KeyIndex или Index срезается 
    """
    # Регулярное выражение для выделения ключа и параметров из файла
    match_string = r'[A-z]+([0-9]+)=(.*)'

    # Валидация аргументов
    if not isfile(filepath):
        raise ValueError("File not found!")

    # Переменные
    filepath = Path(filepath)

    with open(filepath, 'r') as file:
        keys_file = file.read().splitlines()
        keys = {}
        keystring_array = []
        format_type = None

        for line in keys_file:
            match_result = match(match_string, line)

            if match_result:
                key_index = match_result.group(1)
                key_value = match_result.group(2)
                keys.setdefault(key_index, []).append(key_value)

        for val in keys.values():
            keystring_array.append(
                ','.join(val[:-1]).replace("off", "0").replace("on", "1")
            )

        format_type = 'MIFARE' if len(keys[tuple(keys)[0]]) > 3 else 'RFID'

        return tuple(keystring_array), format_type


def create_key_module_based_on_panel_type(
    ip=None,
    username=None,
    password=None,
):
    """
    Мы заранее не знаем какой модуль на панели
    RFID или MIFARE, мы вызываем первый из них, если получаем исключение
    значит нам необходим второй.

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.

    Returns:
        MifareModule || RfidModule: модуль для взаимодействия с ключами

    Raises:
        ValueError: Если не указан ip адрес панели
    """
    # Валидация аргументов
    if ip is None:
        raise ValueError("IP not specified")

    # Переменные
    if username is None or password is None:
        username, password = check_or_brut_admin_credentials(ip, username, password)
    client = BewardClient(ip=ip, login=username, password=password)

    def _create_module(module_cls):
        module = module_cls(client=client, ip=ip, login=username, password=password)
        module.load_params_without_keys()
        return module

    try:
        keys_module = _create_module(MifareModule)
    except BewardIntercomModuleError:
        keys_module = _create_module(RfidModule)

    return keys_module


def upload_keys_from_eqm_file(
    ip=None,
    username=None,
    password=None,
    filepath=None
):
    """
    Загрузка ключей на панель из файлов формата системы EQM

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь к файлу. По умолчанию None.

    Returns:
        bool: Статус загрузки (True или False)

    Raises:
        ValueError: Если не указан IP адрес панели или если файл не найден
    """
    # Валидация аргументов
    if not filepath:
        raise ValueError("Filepath not specified")

    if not isfile(filepath):
        raise ValueError("File not found!")

    print("Загрузка файла с ключами из %s на панель %s" % (filepath, ip))

    # Переменные
    try:
        print("Создание модуля ключей на основе типа панели")
        keys_module = create_key_module_based_on_panel_type(ip, username, password)

        print("Форматирование файла ключей в массив ключей")
        keys, _ = format_keysfile_to_keystring_array(filepath)
    except:
        print("Ошибка загрузки на %s" % ip)
        return False
    
    keys_module.loads_keys(keys, "KEYSTRING")
    keys_module.upload_keys()

    print("Файл с ключами успешно загружен на панель %s" % ip)
    return True


def dump_keys_to_json(
    ip=None,
    username=None,
    password=None,
    filepath=".",
    format_type="MIFARE"
):
    """
    Скачивание ключей с панели в JSON формате

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь сохранения файла. По умолчанию ".".
        format_type(str): формат ключей RFID | MIFARE

    Returns:
        bool: True, если успешно сохранены ключи, иначе False.

    """
    try:
        print("Создание модуля ключей на основе типа панели")
        keys_module = create_key_module_based_on_panel_type(ip, username, password)
        
        print("Загрузка параметров модуля")
        keys_module.load_params()
    except:
        print("Ошибка загрузки параметров модуля")
        return False

    filepath = Path(filepath)
    filename = "%s-keys-dump.json" % ip
    filepath = filepath / filename
    
    try:
        print("Сохранение ключей в JSON формате")
        with open(filepath, 'w') as jsonfile:
            dump(keys_module.dump_keys(format_type), jsonfile)
    except:
        print("Ошибка сохранения ключей в JSON формате")
        return False
    
    print("Ключи успешно сохранены в файле JSON: %s" % filepath)
    return True


def load_keys_from_json(
    ip=None,
    username=None,
    password=None,
    filepath=None
):
    """
    Загрузка ключей на панель из JSON файла

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь к файлу. По умолчанию None.

    Returns:
        bool: True, если ключи успешно загружены.

    Raises:
        ValueError: Если `file_path` не указан или файл не найден.
        ValueError: Если JSON-файл ключей некорректен.
    """
    # Валидация аргументов
    if not filepath:
        raise ValueError("Filepath not specified")

    if not isfile(filepath):
        raise ValueError("File not found!")

    print("Загрузка ключей с панели из JSON файла: %s" % filepath)

    with open(filepath, "r") as file:
        json_file = load(file)

    keys = json_file.get("Keys")
    if not keys:
        raise ValueError("JSON keys file is not correct")

    try:
        print("Создание модуля ключей на основе типа панели")
        keys_module = create_key_module_based_on_panel_type(ip, username, password)

        print("Загрузка ключей на панель")
        keys_module.loads_keys(json_file["Keys"], "KEYPARAMS")
        keys_module.upload_keys()
    except:
        print("Ошибка загрузки ключей на панель")
        return False

    print("Ключи успешно загружены на панель")
    return True


def parse_arguments():
    # Создание парсера аргументов
    general_description = """Управление ключами для панели\n
    eqmup - Загрузить ключи на панель из EQM файла
    d2j   - Выгрузить ключи с панели в JSON
    lj    - Загрузить ключи на панель из JSON
    """
    parser = argparse.ArgumentParser(
        description=general_description,
        epilog=get_epiloge_message("1.0", "Nikita Vasilev (catemohi@gmail.com)",
                                   "03.11.2023"),
        add_help=False,  # Отключает стандартную опцию -h, --help
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Добавление опции на русском языке
    parser.add_argument('-h', '--help', action='help', help='Показать это сообщение и выйти')

    # Создание группы для аргументов с описанием на русском языке
    group = parser.add_argument_group(title='Опции')

    # Подкоманды
    subparsers = parser.add_subparsers(title="Доступные команды", dest="command")

    # Команда для загрузки ключей на панель из EQM
    parser_upload = subparsers.add_parser(
        "eqmup",
        description="Загрузить ключи на панель из EQM файла",
        epilog="Пример: python module_name.py eqmup <IP> --filepath путь/к/файлу",
        add_help=False  # Отключает стандартную опцию -h, --help
    )
    parser_upload.add_argument("ip", help="IP адрес панели")
    parser_upload.add_argument("--username", help="Имя пользователя")
    parser_upload.add_argument("--password", help="Пароль пользователя")
    parser_upload.add_argument("--filepath", help="Путь к файлу с ключами")
    parser_upload.add_argument('-h', '--help', action='help', help='Показать это сообщение и выйти')

    # Команда для выгрузки ключей с панели в JSON
    parser_dump = subparsers.add_parser(
        "d2j",
        description="Выгрузить ключи с панели в JSON",
        epilog="Пример: python module_name.py d2j <IP> --filepath путь/к/файлу",
        add_help=False  # Отключает стандартную опцию -h, --help
    )
    parser_dump.add_argument("ip", help="IP адрес панели")
    parser_dump.add_argument("--username", help="Имя пользователя")
    parser_dump.add_argument("--password", help="Пароль пользователя")
    parser_dump.add_argument("--filepath", help="Путь сохранения файла", default='.')
    parser_dump.add_argument("--format_type", choices=["RFID", "MIFARE"], default="MIFARE", help="Формат ключей")
    parser_dump.add_argument('-h', '--help', action='help', help='Показать это сообщение и выйти')

    # Команда для загрузки ключей на панель из JSON
    parser_load = subparsers.add_parser(
        "lj",
        description="Загрузить ключи на панель из JSON",
        epilog="Пример: python module_name.py lj <IP> --filepath путь/к/файлу",
        add_help=False  # Отключает стандартную опцию -h, --help
    )
    parser_load.add_argument("ip", help="IP адрес панели")
    parser_load.add_argument("--username", help="Имя пользователя")
    parser_load.add_argument("--password", help="Пароль пользователя")
    parser_load.add_argument("--filepath", help="Путь к файлу")
    parser_load.add_argument('-h', '--help', action='help', help='Показать это сообщение и выйти')

    # Обработка аргументов
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    command = None
    args = vars(args)
    command = args.pop('command')

    if command == "eqmup":
        if args['filepath'] is None:
            print("Ошибка! Команде %s необходим путь до исходного EQM файла." % command)
        command = upload_keys_from_eqm_file
        
    elif command == "d2j":
        command = dump_keys_to_json

    elif command == "lj":
        if args['filepath'] is None:
            print("Ошибка! Команде %s необходим путь до исходного JSON файла." % command)
        command = dump_keys_to_json

    command(**args)

if __name__ == "__main__":
    main()