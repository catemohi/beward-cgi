#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class NtpModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi textoverlay_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/ntp_cgi",
    ):
        super(NtpModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "NtpModule"
