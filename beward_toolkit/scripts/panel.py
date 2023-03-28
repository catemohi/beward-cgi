#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import ping

from beward_cgi.audio import AudioModule
from beward_cgi.general.client import BewardClient
from beward_cgi.general.dump_creator import JSONDumpFormatter, make_dumps
from beward_cgi.ntp import NtpModule
from beward_cgi.sip import SipModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов для панели"""


def make_dump(ip=None, username=None, password=None, formatter=JSONDumpFormatter):
    """Получение прав пользователей
    Args:
        ip(str): IP адрес. По умолчанию None.
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    print("Make dump for %s" % ip)
    if ip is None:
        raise ValueError("IP not specified")
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    config = {}
    client = BewardClient(ip=ip, login=username, password=password)
    for module in [NtpModule, AudioModule, SipModule]:
        module_client = module(client=client)
        module_client.load_params()
        config.update(module_client.get_dump(raw=True))
    dump_config = make_dumps(config, formatter)
    return dump_config


if __name__ == "__main__":
    print(make_dump(ip="10.80.1.200"))
