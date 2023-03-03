#!/usr/bin/python
# coding=utf8
from ipaddress import ip_network
from json import load
from os import getenv
from os.path import isfile
from pathlib import Path
from sys import path

from pykeepass import PyKeePass

"""Модуль настроек пакета.
"""
# Родительский пакет
BASE_DIR = Path(__file__).resolve().parent.parent
# Добавление родительского пакета в path
if BASE_DIR not in path:
    path.append(BASE_DIR)
# Настройки базы паролей
PASSWORDS = {
    "path": Path(BASE_DIR, "config", "database.kdbx"),
    "password": getenv("MASTER_KEY"),
    "entries_groups": {
        "admin": "AdminCredentials",
        "gmc": "GmcCredentials",
        "user": "UserCredentials",
    },
}
# Загрузить диапазоны ip адресов
NETWORKS = Path(BASE_DIR, "config", "networks.json")
HOSTS = []
if isfile(NETWORKS):
    with open(NETWORKS, "r") as f:
        NETWORKS = load(f)
        for network in NETWORKS:
            HOSTS += list(ip_network(network).hosts())
# Инициализация базы паролей
if isfile(PASSWORDS["path"]):
    PASSWORDS_BASE = PyKeePass(PASSWORDS["path"], PASSWORDS["password"])
