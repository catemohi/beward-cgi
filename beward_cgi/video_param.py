#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class VideoParameterModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi videoparameter_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/videoparameter_cgi",
    ):
        super(VideoParameterModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "VideoParameterModule"
