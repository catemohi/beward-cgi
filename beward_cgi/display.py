#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class DisplayModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi display_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/display_cgi",
    ):
        super(DisplayModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "DisplayModule"
