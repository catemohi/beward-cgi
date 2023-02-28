#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .rfid import RfidModule

LOGGER = getLogger(__name__)


class ExtrfidModule(RfidModule):
    """Модуль взаимодействия с cgi mifare_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/mifare_cgi",
    ):
        super(ExtrfidModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )
        self.format_type = "MIFARE"

    def __str__(self):
        return "ExtrfidModule"
