#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class VideoOtherModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi videoother_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/videoother_cgi",
    ):
        super(VideoOtherModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "VideoOtherModule"
