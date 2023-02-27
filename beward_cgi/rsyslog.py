#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class RsyslogModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi rsyslog_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/rsyslog_cgi",
    ):
        super(RsyslogModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )

    def __str__(self):
        return "RsyslogModule"
