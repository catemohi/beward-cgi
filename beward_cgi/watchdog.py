#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class WatchdogModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi textoverlay_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/watchdogip_cgi",
    ):
        super(WatchdogModule, self).__init__(client, ip, login, password, cgi)
