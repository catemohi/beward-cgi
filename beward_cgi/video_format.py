#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class VideoFormatModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi videoformat_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/videoformat_cgi",
    ):
        super(VideoFormatModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "VideoFormatModule"
