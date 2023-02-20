#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .general.module import BewardIntercomModule, BewardIntercomModuleError

LOGGER = getLogger(__name__)


class ApartmentModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi apartment_cgi"""

    doorcode_param_name = "DoorCode"
    regcode_param_name = "RegCode"

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/apartment_cgi",
        apartment_number="1",
    ):
        self.apartment_number = apartment_number
        super(ApartmentModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(
            setting=self.cgi,
            params={
                "action": "get",
                "Number": self.apartment_number,
            },
        )

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        for key, value in content.items():
            if "message" in key:
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        params = self.get_params()
        params["action"] = "set"
        params["Number"] = self.apartment_number
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            raise BewardIntercomModuleError("Error, %s" % response.status_code)

        LOGGER.debug("", response)
        return True

    def generate_code(
        self,
        code_param_name,
    ):
        """Метод перегенерации кода открытия дверей и регистрации ключей
        на квартире."""

        params = self.get_params()
        params["action"] = "set"
        params[code_param_name] = "generate"
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            raise BewardIntercomModuleError("Error, %s" % response.status_code)

        self.load_params()
        LOGGER.debug("", response)
        return True


class ApartmentsModule(BewardIntercomModule):
    """Модуль взаимодействия со списками квартир через cgi apartment_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/apartment_cgi",
    ):
        super(ApartmentsModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(
            setting=self.cgi,
            params={
                "action": "list",
            },
        )

        response = self.client.parse_response(response)
        content = response.get("content", {})
        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        appartments_nums = [content[item] for item in content if "Number" in item]
        for num in appartments_nums:
            app = ApartmentModule(client=self.client, apartment_number=num)
            app.load_params()
            self.__dict__["app_" + num] = app

    def get_params(self):
        """Получить параметры с панели."""
        params = {}
        for key, value in self.__dict__.items():
            if key[:4] == "app_":
                params.update({key[4:]: value.get_params()})
        return params

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        for key, value in self.__dict__.items():
            if key[:4] == "app_":
                value.set_params()

        return True

    def update_params(self, update=None, appartment_nums=(), *args, **kwargs):
        """Обновление параметров модуля.
        Args:
            update: параметры для обновления.
            appartment_nums: номера квартир к которым применить настройки.
        Returns:
            bool: True если обновление прошло успешно.
        Raises:
            BewardIntercomModuleError: если обновление прошло не успешно.
        """

        if update is None:
            update = {}
        for appartment_num in appartment_nums:
            app = self.__dict__.get("app_" + appartment_num)
            app.update_params(update=update)

        return self.set_params()
