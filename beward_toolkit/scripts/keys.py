#!/usr/bin/python
# coding=utf8
from os.path import isfile
from re import findall
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


def formating_keysfile_to_keystring_array(filepath):
    match_string = r'[A-z]+([0-9]+)=(.*)'
    if not isfile(filepath):
        raise ValueError("File not found!")
    with open(filepath, 'r') as file:
        keys_file = file.read().splitlines()
        match_result_list = []
        keys = {}
        keystring_array = []
        format_type = None

        for line in keys_file:
            match_result_list.append(findall(match_string, line))

        for line in match_result_list:
            if not line:
                continue
            if line[0][0] not in keys:
                keys[line[0][0]] = [line[0][1]]
                continue
            keys[line[0][0]].append(line[0][1])

        for key, val in keys.items():
            keystring_array.append(','.join(val[:-1]))

        if len(keys[tuple(keys)[0]]) > 2: 
            format_type = 'MIFARE'
        else:
            format_type = 'RFID'

        return tuple(keystring_array), format_type


def upload_keys_from_file(ip=None, username=None, password=None, filepath=None):
    # Валидация аргументов
    if ip is None:
        raise ValueError("IP not specified")
    if filepath is None:
        raise ValueError("Filepath not specified")
    if not isfile(filepath):
        raise ValueError("File not found!")
    if any([username is None, password is None]):
        username, password = check_or_brut_admin_credentials(
            ip,
            username,
            password,
        )
    # Переменные
    client = BewardClient(ip=ip, login=username, password=password)
    keys, format_type = formating_keysfile_to_keystring_array(filepath)
    try:
        keys_module = MifareModule(
            client=client, ip=ip,
            login=username, password=password)
        keys_module.load_params()
    except BewardIntercomModuleError:
        keys_module = RfidModule(
            client=client, ip=ip,
            login=username, password=password)
        keys_module.load_params()
    keys_module.loads_keys(keys, "KEYSTRING")
    keys_module.upload_keys()
