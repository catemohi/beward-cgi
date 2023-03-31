#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class GateModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi gate_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/gate_cgi",
    ):
        super(GateModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "GateModule"
