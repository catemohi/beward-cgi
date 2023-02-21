#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .general.module import BewardIntercomModule, BewardIntercomModuleError

LOGGER = getLogger(__name__)


class RfidModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi rfid_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/rfid_cgi",
    ):
        super(RfidModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )
