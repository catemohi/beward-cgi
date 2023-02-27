#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class RtspParameterModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi rtsp_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/rtsp_cgi",
    ):
        super(RtspParameterModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "RtspParameterModule"
