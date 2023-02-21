#!/usr/bin/python
# coding=utf8
from io import BytesIO
from logging import getLogger
from pickle import dump
from time import time

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
        self.format_type = "RFID"
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
            if not content[item]:
                continue
            try:
                self.__dict__["key_" + str(num)] = Key(content[item])
            except ValueError as err:
                LOGGER.warning("Error init key <{}>: {}".format(content[item], err))
            except TypeError as err:
                LOGGER.warning("Error init key <{}>: {}".format(content[item], err))

    def get_keys(self, format_type):
        """Получить базу ключей.

        Args:
            format_type (Union[Literal["MIFARE"], Literal["RFID"]]): формат
            ключей.
        """
        keys = []
        for key, value in self.__dict__.items():
            if key[:4] == "key_":
                keys.append(value.get_params(format_type))
        return tuple(keys)

    def upload_keys(self):
        """Загрузка ключей на панель
        Args:
            format_type (Union[Literal["MIFARE"], Literal["RFID"]]): формат
            ключей.
        """
        buf = BytesIO()
        for key, value in self.__dict__.items():
            if key[:4] == "key_":
                buf.write(
                    (value.get_key_string(self.format_type) + "\n").encode("utf-8"),
                )
        buf.seek(0)
        response = self.client.query_post(
            setting=self.cgi,
            params={"action": "import"},
            files=buf,
        )
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        return True

    def dump_module(self):
        filename_formatter = "{time}-{ip}.pickle"
        filename = filename_formatter.format(time=int(time()), ip=self.client.ip)
        with open(filename, "wb") as f:
            dump(self, f)
