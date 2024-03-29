#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class ControllerModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi controller_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/controller_cgi",
    ):
        super(ControllerModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "ControllerModule"
