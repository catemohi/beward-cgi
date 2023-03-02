#!/usr/bin/python
# coding=utf8
from os import getenv
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
# Инициализация базы паролей
PASSWORDS_BASE = PyKeePass(PASSWORDS["path"], PASSWORDS["password"])
