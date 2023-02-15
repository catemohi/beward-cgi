#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


class AudioModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi audio_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/audio_cgi",
    ):
        super(AudioModule, self).__init__(client, ip, login, password, cgi)
