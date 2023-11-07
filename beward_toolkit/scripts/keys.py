#!/usr/bin/python3
# coding=utf8
import argparse
from os.path import isfile
from re import match
from pathlib import Path
from sys import path
from json import load, dump, loads
from time import time

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
from interface import HOST_PARSER, CREDENTIALS_PARSER, HELP_PARSER
from interface import LIST_PARSER, STRING_PARSER, ZIP_PARSER
from general_solutions import create_temp_dir, cleanup_temp_dir, create_zip, process_host_arguments
from general_solutions import ping, extract_zip, is_valid_ipv4, run_command_to_seqens


"""
Модуль для взаимодействия с панелью через ключи RFID и MIFARE.

Этот модуль предоставляет функции, обеспечивающие взаимодействие с панелью с использованием ключей
RFID или MIFARE. Он позволяет выполнять загрузку и выгрузку ключей, а также поддерживает работу
с ключами в многопоточном режиме.

Функции:
- format_keysfile_to_keystring_array: Конвертирует данные из файла с ключами EQM в массив ключей.
- create_key_module_based_on_panel_type: Создает модуль для работы с ключами в зависимости от типа панели.
- upload_keys_from_eqm_file: Загружает ключи на панель из файла формата EQM.
- dump_keys_to_json: Сохраняет ключи с панели в формате JSON.
- load_keys_from_json: Загружает ключи на панель из JSON файла.
- import_keys_from_zip_to_panel: Загружает ключи на панель из ZIP-архива.
- add_key: Добавляет отдельный ключ к панели.
- remove_key: Удаляет отдельный ключ с панели.

Основные вызываемые функции:
- `format_keysfile_to_keystring_array` может быть использована для преобразования файла ключей
  в массив строк, готовых к загрузке на панель.
- `create_key_module_based_on_panel_type` создает нужный экземпляр модуля взаимодействия с ключами
  RFID или MIFARE на основе детектирования типа панели.
- `upload_keys_from_eqm_file` выполняет загрузку ключей на панель из указанного файла EQM,
  поддерживая многопоточность.
- `dump_keys_to_json` позволяет выгрузить ключи с панели и сохранить их в JSON файле.
- `load_keys_from_json` загружает ключи на панель из JSON файла, поддерживая многопоточность.
- `import_keys_from_zip_to_panel` обрабатывает ZIP-архив с конфигурационными файлами ключей и 
  выполняет пакетную загрузку на указанные в именах файлов панели.

Пример использования:
```python
# Пример загрузки ключей из файла EQM на панель:
upload_keys_from_eqm_file(ip="192.168.1.100", username="admin", password="password", filepath="keys.eqm")

# Пример выгрузки ключей с панели в JSON файл:
dump_keys_to_json(ip="192.168.1.100", username="admin", password="password", filepath=".", format_type="MIFARE")

# Пример загрузки ключей на панель из JSON файла:
load_keys_from_json(ip="192.168.1.100", username="admin", password="password", filepath="keys.json")

# Пример импорта ключей из ZIP-архива:
import_keys_from_zip_to_panel(archive_path="keys_archive.zip")

# TODO: Реализовать примеры использования add_key и remove_key после их реализации.
# TODO: добавить функцию add_key()
# TODO: добавить функцию remove_key()
# TODO: добавить команду add
# TODO: добавить команду remove
"""


MODULE_VERSION = "1.2"


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


def _load_keys(filepath, filetype):
    """
    Загружает ключи из файла в зависимости от типа файла.

    Args:
        filepath (str): Путь к файлу с ключами.
        filetype (str): Тип файла: "JSON" или "CONF".

    Returns:
        List[str]: Список загруженных ключей.

    Raises:
        ValueError: Если файл не найден или JSON файл содержит некорректные ключи.

    Note:
        Для типа "JSON" файл должен содержать ключи в формате JSON в поле "Keys".
        Для типа "CONF" файл должен содержать ключи в формате текста.

    """
    keys = []

    if filetype == "JSON":
        if not isfile(filepath):
            raise ValueError("File not found!")

        print("Загрузка ключей с панели из JSON файла: %s" % filepath)

        with open(filepath, "r") as file:
            json_file = load(file)
        keys = json_file.get("Keys")

        if not keys:
            raise ValueError("JSON keys file is not correct")

    elif filetype == "CONF":
        if not isfile(filepath):
            raise ValueError("File not found!")

        print("Загрузка файла с ключами из %s" % filepath)
        keys, _ = format_keysfile_to_keystring_array(filepath)
        try:
            print("Форматирование файла ключей в массив ключей")
            keys, _ = format_keysfile_to_keystring_array(filepath)
        except:
            print("Ошибка формирования списка ключей из файла %s" % filepath)
            return False

        if not keys:
            print("Ошибка! Список ключей пуст.")
            return False

    return keys


def upload_keys_from_eqm_file(
    ip=None,
    username=None,
    password=None,
    filepath=None,
    keys = None,
    func="host",
    **kwargs
):
    """
    Загрузка ключей на панель из файлов формата системы EQM

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь к файлу. По умолчанию None.
        keys (list): Сформированный список ключей. По умолчанию None.
        func (str): режим работы доступны host | string | list. По умолчанию "host".
        kwargs (dict): оставшиеся аргументы режимов работ

    Returns:
        bool: Статус загрузки (True или False)

    Raises:
        ValueError: Если не указан IP адрес панели или если файл не найден
    """
    # Валидация аргументов
    if not filepath and not keys:
        raise ValueError("Filepath and keys not specified")

    if not keys:
        keys = _load_keys(filepath, "CONF")

    if func in ("string", "list"):
        output = process_host_arguments(upload_keys_from_eqm_file,
                                        kwargs.get("csvpath", kwargs.get("string")),
                                        {"ip": "", "username": username, "password": password, "keys": keys, "func": "host"},
                                        ("ip", "username", "password", "keys", "func"),
                                        kwargs.get("thread"))
        return True
    # Переменные
    try:
        print("Создание модуля ключей на основе типа панели %s" % ip)
        keys_module = create_key_module_based_on_panel_type(ip, username, password)
    except:
        print("Ошибка загрузки на %s" % ip)
        return False
    
    keys_module.load_keys_from_panel()
    keys_module.loads_keys(keys, "KEYSTRING")
    keys_module.upload_keys()

    print("Файл с ключами успешно загружен на панель %s" % ip)
    return True


def dump_keys_to_json(
    ip=None,
    username=None,
    password=None,
    filepath=".",
    format_type="MIFARE",
    func="host",
    raw=False,
    **kwargs
):
    """
    Скачивание ключей с панели в JSON формате

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь сохранения файла. По умолчанию ".".
        format_type (str): формат ключей RFID | MIFARE. По умолчанию "MIFARE".
        func (str): режим работы доступны host | string | list. По умолчанию "host". 
        raw (bool): сохранять ли файл или вернуть ключи в сыром формате на выход. По умолчанию False. 
        kwargs (dict): оставшиеся аргументы режимов работ

    Returns:
        bool: True, если успешно сохранены ключи, иначе False.

    """

    def _save_dump(ip, filepath, output):
        filepath = Path(filepath)
        filename = "%s-keys-dump.json" % ip
        filepath = filepath / filename
        try:
            print("Сохранение ключей в JSON формате")
            with open(filepath, 'w') as jsonfile:
                output = loads(output)
                dump(output, jsonfile)
        except:
            print("Ошибка сохранения ключей в JSON формате")
            return False

        print("Ключи успешно сохранены в файле JSON: %s" % filepath)
        print("Путь до файла: %s" % filepath.resolve())
        return filepath.resolve()

    if func in ("string", "list"):
        output = process_host_arguments(dump_keys_to_json,
                                        kwargs.get("csvpath", kwargs.get("string")),
                                        {"ip": "", "username": username, "password": password, "filepath": filepath, "format_type": format_type, "func": "host", "raw": True},
                                        ("ip", "username", "password", "filepath", "format_type", "func","raw"),
                                        kwargs.get("thread"))
        path_collection = []
        for item in output:
            path_collection.append(_save_dump(item[0]['ip'], item[0]['filepath'], item[1]))

        if kwargs['archiveted']:
            archive_name = "keys-dump-archive-{}".format(int(time()))
            _, path_to_archive = create_zip(name=archive_name, zip_path=filepath,
                                            files_path_collection=path_collection,
                                            remove_files=True)
            return path_to_archive

        return True
                

    try:
        print("Создание модуля ключей на основе типа панели %s" % ip)
        keys_module = create_key_module_based_on_panel_type(ip, username, password)
        
        print("Загрузка параметров модуля")
        keys_module.load_params()
    except:
        print("Ошибка загрузки параметров модуля")
        return False

    output = keys_module.dump_keys(format_type)
    if raw:
        return output
    else:
        _save_dump(ip, filepath, output)
        return True


def load_keys_from_json(
    ip=None,
    username=None,
    password=None,
    filepath=None,
    keys=None,
    func="host",
    **kwargs
):
    """
    Загрузка ключей на панель из JSON файла

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь к файлу. По умолчанию None.
        keys (dict): Форматировнный словарь ключей. По умолчанию None.
        func (str): режим работы доступны host | string | list. По умолчанию "host".
        kwargs (dict): оставшиеся аргументы режимов работ

    Returns:
        bool: True, если ключи успешно загружены.

    Raises:
        ValueError: Если `file_path` не указан или файл не найден.
        ValueError: Если JSON-файл ключей некорректен.
    """
    # Валидация аргументов
    if not filepath and not keys:
        raise ValueError("Filepath and keys not specified")

    if not keys:
        keys = _load_keys(filepath, "JSON")

    if func in ("string", "list"):
        output = process_host_arguments(load_keys_from_json,
                                        kwargs.get("csvpath", kwargs.get("string")),
                                        {"ip": "", "username": username, "password": password, "keys": keys, "func": "host"},
                                        ("ip", "username", "password", "keys", "func"),
                                        kwargs.get("thread"))

    try:
        print("Создание модуля ключей на основе типа панели %s" % ip)
        keys_module = create_key_module_based_on_panel_type(ip, username, password)

        print("Загрузка ключей на панель")
        keys_module.loads_keys(keys, "KEYPARAMS")
        keys_module.upload_keys()
    except:
        print("Ошибка загрузки ключей на панель, возможно ключи загрузились не полностью")
        return False

    print("Ключи успешно загружены на панель")
    return True


def import_keys_from_zip_to_panel(archive_path):
    """
    Разархивирует архив во временную директорию.
    Читает имена файлов внутри временной директории, проверяет их на допустимость
    IPv4 адресов и выполняет загрузку ключей для каждого адреса.

    Args:
        archive_path (str): Путь к ZIP-архиву.
        
    Raises:
        ValueError: Если формат файла не поддерживается (допустимые форматы: json или conf).

    Note:
        Файл должен иметь один из следующих форматов:
        - Файл в формате CONF: <ip_address>.conf (например, 10.80.1.200.conf)
          Пример содержимого файла .conf:
          ```
          [KEYS]
          KeyValue1=000000C2137B42
          KeyApartment1=0
          KeyIndex1=0
          KeyValue2=000000C21252E2
          ```
        - Файл в формате JSON: <ip_address>.json (например, 10.80.1.200.json)
          Пример содержимого файла .json:
          ```
          "{\"Keys\": [{\"Key\": \"000000034D9502\",\"Apartment\": \"0\"}]}"
          ```
    """
    temp_dir = Path(create_temp_dir())
    count_files = extract_zip(archive_path, temp_dir)
    print("Разархивировано %s файлов из архива %s во временную папку." % (count_files, archive_path))
    files = temp_dir.glob('*')

    for file_path in files:
        splited_file_name = file_path.name.split('.')
        ip, file_format = '.'.join(splited_file_name[:-1]), splited_file_name[-1]

        if not is_valid_ipv4(ip):
            print("Ошибка! Имя файла %s содержит некорректный IP-адрес: %s." % (file_path.name, ip))
            continue
        if not ping(ip):
            print("Ошибка! IP-адрес %s недоступен." % ip)
            continue

        if file_format.lower() == "json":
            command = load_keys_from_json
        elif file_format.lower() == "conf":
            command = upload_keys_from_eqm_file
        else:
            raise ValueError("Ошибка! Формат файла %s не поддерживается. Допустимые форматы: json или conf." % file_format)
            continue

        try:
            command(ip=ip, filepath=file_path)
        except Exception as e:
            print("Ошибка загрузки ключей на панель %s: %s" % (ip, str(e)))

    cleanup_temp_dir(temp_dir)


def parse_arguments():
    # Создание парсера аргументов
    general_description = """Управление ключами для панели\n
    eqmup - Загрузить ключи на панель из EQM файла
    d2j   - Выгрузить ключи с панели в JSON
    lj    - Загрузить ключи на панель из JSON
    zipup - Загрузить ключи на панель из ZIP-архива
    """
    parser = argparse.ArgumentParser(
        description=general_description,
        epilog=get_epiloge_message(MODULE_VERSION, "Nikita Vasilev (catemohi@gmail.com)",
                                   "04.11.2023"),
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

    # Команда для загрузки ключей на панель из ZIP-архива
    parser_zip = subparsers.add_parser(
        "zipup",
        description="Загрузить ключи на панель из ZIP-архива",
        epilog="Пример: python module_name.py zipup <путь_к_архиву>",
        add_help=False  # Отключает стандартную опцию -h, --help
    )
    parser_zip.add_argument("archive_path", help="Путь к ZIP-архиву с ключами")
    parser_zip.add_argument('-h', '--help', action='help', help='Показать это сообщение и выйти')

    # Команда для выгрузки ключей с панели в JSON
    parser_dump = subparsers.add_parser(
        "d2j",
        description="Выгрузить ключи с панели в JSON",
        epilog="Пример: python module_name.py d2j <IP> --filepath путь/к/файлу",
        add_help=False,  # Отключает стандартную опцию -h, --help
        parents=[HELP_PARSER]
    )

    # Типы работы d2j
    dump_subparsers = parser_dump.add_subparsers(title="Доступные типы работы")

    # Общие аргументы для всех типов работы d2j
    general_dump_parser = argparse.ArgumentParser(add_help=False)
    general_dump_parser.add_argument("--filepath", help="Путь сохранения файла", default='.')
    general_dump_parser.add_argument("--format_type", choices=["RFID", "MIFARE"], default="MIFARE", help="Формат ключей")

    # Работа с один хостом
    parser_host = dump_subparsers.add_parser('host', help='запуск скрипта для одного адреса',
                                        parents=[CREDENTIALS_PARSER,
                                                 HOST_PARSER,
                                                 general_dump_parser,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_host.set_defaults(func="host")

    # Работа с группой хостов из csv файла
    parser_list = dump_subparsers.add_parser('list', help=("запуск скрипта для списка"
                                                      " адресов из csv файла."),
                                        parents=[CREDENTIALS_PARSER,
                                                 LIST_PARSER,
                                                 general_dump_parser,
                                                 ZIP_PARSER,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_list.set_defaults(func="list")

    # Работа с группой хостов из строки
    parser_string = dump_subparsers.add_parser('string',
                                          help=("запуск скрипта для списка"
                                                "адресов из текстовой линии."),
                                          parents=[CREDENTIALS_PARSER,
                                                   STRING_PARSER,
                                                   general_dump_parser,
                                                   ZIP_PARSER,
                                                   HELP_PARSER],
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_string.set_defaults(func="string")

    # Команда для загрузки ключей на панель из JSON
    parser_load = subparsers.add_parser(
        "lj",
        description="Загрузить ключи на панель из JSON",
        epilog="Пример: python module_name.py lj <IP> --filepath путь/к/файлу",
        add_help=False,  # Отключает стандартную опцию -h, --help
        parents=[HELP_PARSER]
    )
    # Создание общего парсера для всех типов работы команды
    general_parser_load = argparse.ArgumentParser(add_help=False)
    general_parser_load.add_argument("filepath", help="Путь к JSON файлу ключей")

    # Типы работы lj
    load_subparsers = parser_load.add_subparsers(title="Доступные типы работы")

    # Работа с один хостом
    parser_host = load_subparsers.add_parser('host', help='запуск скрипта для одного адреса',
                                        parents=[CREDENTIALS_PARSER,
                                                 HOST_PARSER,
                                                 general_parser_load,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_host.set_defaults(func="host")

    # Работа с группой хостов из csv файла
    parser_list = load_subparsers.add_parser('list', help=("запуск скрипта для списка"
                                                      " адресов из csv файла."),
                                        parents=[CREDENTIALS_PARSER,
                                                 LIST_PARSER,
                                                 general_parser_load,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_list.set_defaults(func="list")

    # Работа с группой хостов из строки
    parser_string = load_subparsers.add_parser('string',
                                          help=("запуск скрипта для списка"
                                                "адресов из текстовой линии."),
                                          parents=[CREDENTIALS_PARSER,
                                                   STRING_PARSER,
                                                   general_parser_load,
                                                   HELP_PARSER],
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_string.set_defaults(func="string")


    # Команда для загрузки ключей на панель из EQM
    parser_eqmup = subparsers.add_parser(
        "eqmup",
        description="Загрузить ключи на панель из EQM файла",
        epilog="Пример: python module_name.py eqmup <IP> --filepath путь/к/файлу",
        add_help=False,  # Отключает стандартную опцию -h, --help
        parents=[HELP_PARSER]
    )
    # Создание общего парсера для всех типов работы команды
    general_parser_eqmup = argparse.ArgumentParser(add_help=False)
    general_parser_eqmup.add_argument("filepath", help="Путь к EQM файлу ключей")

    # Типы работы eqmup
    eqmup_subparsers = parser_eqmup.add_subparsers(title="Доступные типы работы")

    # Работа с один хостом
    parser_host = eqmup_subparsers.add_parser('host', help='запуск скрипта для одного адреса',
                                        parents=[CREDENTIALS_PARSER,
                                                 HOST_PARSER,
                                                 general_parser_eqmup,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_host.set_defaults(func="host")

    # Работа с группой хостов из csv файла
    parser_list = eqmup_subparsers.add_parser('list', help=("запуск скрипта для списка"
                                                      " адресов из csv файла."),
                                        parents=[CREDENTIALS_PARSER,
                                                 LIST_PARSER,
                                                 general_parser_eqmup,
                                                 HELP_PARSER],
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_list.set_defaults(func="list")

    # Работа с группой хостов из строки
    parser_string = eqmup_subparsers.add_parser('string',
                                          help=("запуск скрипта для списка"
                                                "адресов из текстовой линии."),
                                          parents=[CREDENTIALS_PARSER,
                                                   STRING_PARSER,
                                                   general_parser_eqmup,
                                                   HELP_PARSER],
                                          formatter_class=argparse.RawTextHelpFormatter,
                                          add_help=False)  # Отключает стандартную опцию -h, --help)
    parser_string.set_defaults(func="string")

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
        command = load_keys_from_json

    elif command == "zipup":
        command = import_keys_from_zip_to_panel

    command(**args)

if __name__ == "__main__":
    main()