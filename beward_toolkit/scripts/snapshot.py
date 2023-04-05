#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path
from time import time
from datetime import datetime
from re import match

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import get_reachable_hosts, ping, run_command_to_seqens

from beward_cgi.general.client import BewardClient
from beward_cgi.images import ImagesModule
from beward_cgi.ntp import NtpModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов для создания скриншотов с панелей Beward"""

def _get_date_from_datestring(datestring):
    """Получить дату из строки с датой

    Args:
        datestring (_type_): _description_
        pattern (regexp, optional): _description_. Defaults to r"(:?\d{1,2}\.){2}\d{4}".
    """
    date_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})"
    datetime_pattern = r"(\d{1,2})\.(\d{1,2})\.(\d{4})\s(\d{1,2}):(\d{1,2})""
    match_datestring = match(datestring, date_pattern)
    match_datetimestring = match(datestring, datetime_pattern)
    check_date_string = match_datestring is None
    check_datetime_string = match_datetimestring is None
    if all([check_date_string, check_datetime_string]):
        raise ValueError("Invalid datestring! Need format 'DD.MM.YYYY' or 'DD.MM.YYYY HH:MM'")
    datestring = match_datestring.groups()
    

def _get_snapshot_savepath(save_path=".", name=None, file_format="jpeg"):
    """Получить путь сохранения скриншота

    Args:
        name (str, optional): имя скриншота. Defaults to None.
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
    changed_date=None,
):
    """Получение скриншота с панели
    Args:
        ip(str): IP адрес. По умолчанию None.
        username(str): Имя пользователя. По умолчанию None.
        password(str): Пароль пользователя. По умолчанию None.
    """
    print("Get snapshot %s" % ip)
    # Validate
    if ip is None:
        raise ValueError("IP not specified")
    # Brut
    username, password = check_or_brut_admin_credentials(
        ip,
        username,
        password,
    )
    # Variable
    if snapshot_name is None:
        snapshot_name = int(time())

    name_format = "{name}.{file_format}"
    name = name_format.format(name=snapshot_name, file_format=file_format)
    client = BewardClient(ip=ip, login=username, password=password)
    image_client = ImagesModule(client=client)
    ntp_client = NtpModule(client=client)
    # Load parameters from Beward panel
    for module in (ntp_client, image_client):
        module.load_params()
    # Change time to Beward panel
    if changed_date is not None:
        ...

    # Get snapshots
    binary_image = client.get_images(channel, False)
    # Return NTP settings
    if changed_date is not None:
        ...
    # Save snapshot
    if save:
        save_path = _get_snapshot_savepath(save_path, name, file_format)
        with open(save_path, 'wb') as snapshot_file:
            snapshot_file.write(binary_image)
        return True
    # Return raw snapshot
    return (name, binary_image)
