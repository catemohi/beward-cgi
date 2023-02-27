#!/usr/bin/python
# coding=utf8
from io import BytesIO
from logging import getLogger

from .beward_key import Key
from .general.dump_creator import JSONDumpFormatter, make_dump
from .general.dump_loader import JSONDumpLoader, loads_dump
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

    def __str__(self):
        return "RfidModule"

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
                self.__dict__["key_" + str(num)] = Key(key_string=content[item])
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
        response = self.client.query_post(
            setting=self.cgi,
            params={"action": "import"},
            files={"file": ("keys.csv", buf.getvalue())},
            timeout=180,
        )
        response = self.client.parse_response(response)
        content = response.get("content", {})
        if response.get("code") != 200:
            LOGGER.debug(content)
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"] != "OK":
            LOGGER.debug(content)
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        buf.close()
        return True

    def dump_keys(self, format_type="MIFARE", formatter=JSONDumpFormatter):
        """Сохранение ключей.
        Args:
            format_type(str): формат ключей.
            formatter(DumpFormatter): форматирование сохранения.

        """
        keys = self.get_keys(format_type)
        config = {"Keys": keys}
        dump_config = make_dump(config, formatter)
        return dump_config

    def loads_dump_keys(
        self,
        config,
        format_type="MIFARE",
        loader=JSONDumpLoader,
    ):

        """Загрузка сохраненных ключей.
        Args:
            config(dict or str): сохраненая конфигурация.
            format_type(str): формат ключей.
            loader(DumpLoader): форматирование сохранения.
        """
        if isinstance(config, str):
            config = loads_dump(config, loader)
        keys = config.get("Keys", [])
        if not keys:
            LOGGER.warning("No keys found.")
            return
        for num, key in enumerate(keys):
            try:
                self.__dict__["key_" + str(num)] = Key(key_params=key)
            except ValueError as err:
                LOGGER.warning("Error init key <{}>: {}".format(key, err))
            except TypeError as err:
                LOGGER.warning("Error init key <{}>: {}".format(key, err))
