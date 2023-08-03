#!/usr/bin/python
# coding=utf8
from pathlib import Path
from sys import path

if str(Path(__file__).resolve().parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent))
if str(Path(__file__).resolve().parent.parent.parent) not in path:
    path.append(str(Path(__file__).resolve().parent.parent.parent))

from general_solutions import ping

from beward_cgi.apartment import ApartmentsModule
from beward_cgi.audio import AudioModule
from beward_cgi.controller import ControllerModule
from beward_cgi.display import DisplayModule
from beward_cgi.extrfid import ExtrfidModule
from beward_cgi.gate import GateModule
from beward_cgi.general.client import BewardClient
from beward_cgi.general.dump_creator import JSONDumpFormatter, make_dumps
from beward_cgi.https import HttpsModule
from beward_cgi.intercom import IntercomModule
from beward_cgi.intercomdu import IntercomduModule
from beward_cgi.mifare import MifareModule
from beward_cgi.ntp import NtpModule
from beward_cgi.osd_position import OsdPositionModule
from beward_cgi.rfid import RfidModule
from beward_cgi.rsyslog import RsyslogModule
from beward_cgi.rtsp_param import RtspParameterModule
from beward_cgi.sip import SipModule
from beward_cgi.system_info import SystemInfoModule
from beward_cgi.textoverlay import TextOverlayModule
from beward_cgi.user_capabilities import UserCapabilitiesModule
from beward_cgi.video_coding import VideoCodingModule
from beward_cgi.watchdog import WatchdogModule
from beward_toolkit.scripts.credentials import check_or_brut_admin_credentials

"""Модуль скриптов для панели"""

DKS_PANEL = [
    SystemInfoModule,  # дамп работает
    TextOverlayModule, # дамп работает
    IntercomModule,  # дамп работает
    IntercomduModule,  # дамп работает
    VideoCodingModule,  # дамп работает
    WatchdogModule,  # дамп работает
    NtpModule,  # дамп работает
    RsyslogModule,  # дамп работает
    SipModule,  # дамп работает
    RfidModule,  # дамп работает
    MifareModule,
    ExtrfidModule,
    DisplayModule,  # дамп работает
    HttpsModule,  # дамп работает
    UserCapabilitiesModule,  # дамп работает
    GateModule,  # дамп работает
    ApartmentsModule,  # дамп работает
    AudioModule,  # дамп работает
    RtspParameterModule,  # дамп работает
]

DS_PANEL = [
    SystemInfoModule,
    TextOverlayModule,
    VideoCodingModule,
    WatchdogModule,
    NtpModule,
    RsyslogModule,
    SipModule,
    DisplayModule,
    HttpsModule,
    GateModule,
    AudioModule,
    RtspParameterModule,
    ControllerModule,
]


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
    for module in [NtpModule, AudioModule, SipModule, ApartmentsModule, RfidModule, UserCapabilitiesModule]:
        module_client = module(client=client)
        module_client.load_params()
        config.update(module_client.get_dump(raw=True))
    dump_config = make_dumps(config, formatter)
    return dump_config


if __name__ == "__main__":
    print(make_dump(ip="10.80.1.200"))
