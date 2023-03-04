#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import get_reachable_hosts, ping, run_command_to_seqens

from beward_cgi.user_capabilities import UserCapabilitiesModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов с правами пользователя на панели"""


def get_capabilites(ip=None, username=None, password=None):
    """Получение прав пользователей
    Args:
        ip(str): IP адрес. По умолчанию None.
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    print("Get capabilites %s %s/%s" % (ip,username,password))
    if ip is None:
        raise ValueError("IP not specified")
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    client = UserCapabilitiesModule(ip=ip, login=username, password=password)
    client.load_params()
    output = client.get_params()
    client.client.close()
    print("Capabilites for ip %s are caught!" % ip)
    return output


def get_capabilites_hosts(hosts=None, username=None, password=None, thread_num=1):
    """Получить права для списка панелей

    Args:
        hosts (list): Список хостов. По умолчанию None.
        username (str, optional): Имя пользователя. По умолчанию None.
        password (str, optional): Пароль пользователя. По умолчанию None.
        thread_num(int): Количество потоков. По умолчанию 1.
    """
    output = []
    if hosts is not None:
        for host in hosts:
            if not ping(host):
                output.append(({"ip": host}, {"Error": "UNREACHABLE"}))
                output.remove(host)
    else:
        hosts = get_reachable_hosts()
    seqens = [(host, username, password) for host in hosts]
    output += run_command_to_seqens(
        get_capabilites,
        seqens,
        ("ip", "username", "password"),
        thread_num,
    )
    return output


if __name__ == "__main__":
    output = get_capabilites_hosts(thread_num=100)
    with open("capabilites.csv", "w") as f:
        f.write("ip;admin;user1;user2;user3;user4;user5\n")
        for line in output:
            write_line = ""
            input_line, output_line = line
            write_line += "%s;" % input_line["ip"]
            for _, value in output_line.items():
                write_line += "%s;" % value
            f.write(write_line + "\n")
