#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class NetworkModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi network_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/network_cgi",
    ):
        super(NetworkModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "NetworkModule"
