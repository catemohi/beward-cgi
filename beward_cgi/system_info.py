#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class SystemInfoModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi systeminfo_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/systeminfo_cgi",
    ):
        super(SystemInfoModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "SystemInfoModule"
