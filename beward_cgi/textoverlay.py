#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class TextOverlayModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi textoverlay_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/textoverlay_cgi",
    ):
        super(TextOverlayModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "TextOverlayModule"
