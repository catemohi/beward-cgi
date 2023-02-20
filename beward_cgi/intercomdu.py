#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class IntercomduModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi intercomdu_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/intercomdu_cgi",
    ):
        raise NotImplementedError
        super(IntercomduModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )
