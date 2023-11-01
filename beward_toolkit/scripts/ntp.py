#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import get_reachable_hosts, ping, run_command_to_seqens

from beward_cgi.ntp import NtpModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов с правами пользователя на панели"""

def get_ntp_dump(ip=None, username=None, password=None):
    """Получение прав пользователей
    Args:
        ip(str): IP адрес. По умолчанию None.
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    print("Get NTP dump  %s %s/%s" % (ip, username, password))
    if ip is None:
        raise ValueError("IP not specified")
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    client = NtpModule(ip=ip, login=username, password=password)
    client.load_params()
    output = client.get_dump()
    client.client.close()
    return output


if __name__ == "__main__":
    print(get_ntp_dump(ip="10.80.1.200"))
