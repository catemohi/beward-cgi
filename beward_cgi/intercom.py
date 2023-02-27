#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class IntercomModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi intercom_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/intercom_cgi",
    ):
        super(IntercomModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )

    def __str__(self):
        return "IntercomModule"
