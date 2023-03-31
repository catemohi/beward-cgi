#!/usr/bin/python
# coding=utf8
from io import BytesIO
from logging import getLogger

from .beward_key import Key
from .general.dump_creator import JSONDumpFormatter, make_dumps
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
        self.load_keys_from_panel()

    def load_keys_from_panel(self):
        """Получение ключей из панели."""
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
        keys = [value for _, value in content.items() if value]
        self.loads_keys(keys, keys_type="KEYSTRING")

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

    def dump_keys(self, format_type="MIFARE", formatter=JSONDumpFormatter, raw=False):
        """Сохранение ключей.
        Args:
            format_type(str): формат ключей.
            formatter(DumpFormatter): форматирование сохранения.

        """
        keys = self.get_keys(format_type)
        config = {"Keys": keys}
        if raw:
            return config
        dump_config = make_dumps(config, formatter)
        return dump_config

    def loads_keys(self, keys, keys_type="KEYPARAMS"):
        """Загрузка сохраненных ключей.
        Args:
            keys(Sequence[Dict]): Ключи для загрузки.
            keys_type(str[KEYSTRING,KEYPARAMS]): Тип ключей.

        """
        if not keys:
            LOGGER.warning("No keys found.")
            return
        if "is not defined" in " ".join(keys):
            raise BewardIntercomModuleError("Module is not defined")
        for num, key in enumerate(keys):
            try:
                num += 1
                if keys_type == "KEYSTRING":
                    self.__dict__["key_" + str(num)] = Key(key_string=key)
                elif keys_type == "KEYPARAMS":
                    self.__dict__["key_" + str(num)] = Key(key_params=key)
            except ValueError as err:
                LOGGER.warning("Error init key <{}>: {}".format(key, err))
            except TypeError as err:
                LOGGER.warning("Error init key <{}>: {}".format(key, err))

    def add_key(self, key):
        """Добавление ключа.

        Args:
            key (Key): обьект ключа
        """
        if not isinstance(key, Key):
            raise TypeError("Key must be an instance of Key.")
        key_params = key.get_params(self.format_type)
        params = {"action": "add"}
        params.update(key_params)
        response = self.client.query(
            setting=self.cgi,
            params=params,
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

    def slow_upload_keys(self):
        """Загрузка ключей на панель по ключу."""
        for key, value in self.__dict__.items():
            if key[:4] == "key_":
                try:
                    self.add_key(value)
                except BewardIntercomModuleError as err:
                    LOGGER.error(str(err))

    def delete_key(self, key_value=None, apartment=None, key_index=None):
        """Удаление ключей.

        Args:
            key_value (str, optional): Значение ключа. Defaults to None.
            apartment (str, optional): Значение квартиры. Defaults to None.
            key_index (str, optional): Индекс ключа. Defaults to None.
        """
        params = {"action": "delete"}
        if key_value is not None:
            params.update({"Key": key_value})
        if apartment is not None:
            params.update({"Apartment": apartment})
        if key_index is not None:
            params.update({"Index": key_index})
        response = self.client.query(
            setting=self.cgi,
            params=params,
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

    def update_key(self, update_key):

        """Обновление параметров ключа

        Args:
            update_key (Key): обновленный ключ
        """
        params = update_key.get_params(self.format_type)
        params.update({"action": "update"})
        response = self.client.query(
            setting=self.cgi,
            params=params,
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
        self.load_keys_from_panel()

    def get_dump(self, formatter=JSONDumpFormatter, raw=False):
        """Сохранение параметров модуля.
        Args:
            formatter(DumpFormatter): форматирование сохранения.
            raw(bool): Получить обьект как dict
        """
        full_config = {}
        config = super(RfidModule, self).get_dump(formatter, raw)
        keys = self.dump_keys(formatter=formatter, raw=raw)
        if raw:
            full_config.update(config)
            full_config.update(keys)
            return full_config

        full_config = "{" + f"{config},{keys}" + "}"
        return full_config

    def set_dump(self, config):
        """Загрузка параметров модуля.
        Args:
            config(dict): конфигурация панели.

        """
        module_config = config.get(self.__str__(), None)
        if module_config is None:
            raise BewardIntercomModuleError("Module config not found.")

        for key, value in module_config.items():
            check_param = self.__dict__.get("param_" + key, None)
            if check_param is None:
                LOGGER.error("Param %s not found.", key)
                continue
            self.__dict__["param_" + key] = value
            LOGGER.debug("Param %s set to %s.", key, value)
        keys = config.get("Keys", None)
        self.loads_keys(keys)
        return True
