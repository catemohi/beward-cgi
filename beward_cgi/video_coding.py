#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class VideoCodingModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi /videocoding_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/videocoding_cgi",
    ):
        super(VideoCodingModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "VideoCodingModule"
