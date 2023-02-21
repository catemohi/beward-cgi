#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .beward_key import Key
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

    def load_params(self):
        """Метод получения параметров установленных на панели."""
        super(RfidModule, self).load_params()
        response = self.client.query(
            setting=self.cgi,
            params={"action": "export"},
        )
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        for num, item in enumerate(content):
            try:
                self.__dict__["key_" + str(num)] = Key(content[item])
            except ValueError as err:
                LOGGER.warning("Error init key <{}>: {}".format(content[item], err))
            except TypeError as err:
                LOGGER.warning("Error init key <{}>: {}".format(content[item], err))

            print(self.__dict__["key_" + str(num)])
