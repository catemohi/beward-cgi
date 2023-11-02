#!/usr/bin/python
# coding=utf8
from os.path import isfile
from re import match
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from beward_cgi.rfid import RfidModule
from beward_cgi.mifare import MifareModule
from beward_cgi.general.client import BewardClient
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials
from beward_cgi.general.module import BewardIntercomModuleError


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

    # Переменные
    try:
        keys_module = create_key_module_based_on_panel_type(ip, username, password)
        keys, _ = format_keysfile_to_keystring_array(filepath)
    except:
        print("Upload Error to %s" % ip)
        return False
    
    keys_module.loads_keys(keys, "KEYSTRING")
    keys_module.upload_keys()
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

    """
    try:
        keys_module = create_key_module_based_on_panel_type(ip, username, password)
        keys_module.load_params()
    except:
        return False

    filepath = Path(filepath)
    filename = "%s-keys-dump.json" % ip
    filepath = filepath / filename
    with open(filepath, 'w') as jsonfile:
        jsonfile.write(keys_module.dump_keys(format_type))
    return True, filepath.resolve()



def load_keys_from_json(
    ip=None,
    username=None,
    password=None,
    filepath="."
):
    """
    Загрузка ключей на панель из JSON файла

    Args:
        ip (str): IP адрес панели. Обязательный аргумент.
        username (str): Имя пользователя. По умолчанию None.
        password (str): Пароль пользователя. По умолчанию None.
        filepath (str): Путь к файлу. По умолчанию None.

    """
    # Валидация аргументов
    if not filepath:
        raise ValueError("Filepath not specified")

    if not isfile(filepath):
        raise ValueError("File not found!")

    keys_module = create_key_module_based_on_panel_type(ip, username, password)

print(dump_keys_to_json(ip="10.80.1.200"))