#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .capabilities_parser import Capabilities
from .general.module import BewardIntercomModule, BewardIntercomModuleError

LOGGER = getLogger(__name__)


class UserCapabilitiesModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi pwdgrp_cgi правами пользователей"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/pwdgrp_cgi",
    ):
        super(UserCapabilitiesModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        """Метод получения параметров установленных на панели."""
        response = self.client.query(setting=self.cgi, params={"action": "get"})

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        name_category = content.pop("message_0", None)

        if name_category is None:
            raise BewardIntercomModuleError("Unknown parse error.")

        content = [value.split(":") for key, value in content.items() if value]
        content = dict(content)

        for key, value in content.items():
            if key == "message":
                continue

            try:
                self.__dict__["param_" + str(key)] = Capabilities(
                    str(value),
                )
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = Capabilities(value)

    def update_params(self, update=None, *args, **kwargs):
        """Обновление параметров модуля.
        Args:
            update: параметры для обновления.
            Ожидаеться словарь словарей, например:
            {"admin": {"Name": "Value"}}
        Returns:
            bool: True если обновление прошло успешно.
        Raises:
            BewardIntercomModuleError: если обновление прошло не успешно.
        """

        if update is None:
            update = {}
        for key, value in update.items():
            item = self.__dict__.get("param_" + key, None)

            if item is None:
                continue

            if isinstance(value, dict):
                self.__dict__["param_" + key].update_params(update=value)

        return True

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        all_user_params = self.get_params(True)

        for key, value in all_user_params.items():
            params = {"action": "update"}
            params["username"] = key
            params["capabilities"] = value
            response = self.client.query(setting=self.cgi, params=params)

            if response.status_code != 200:
                raise BewardIntercomModuleError("Error, %s" % response.status_code)

            LOGGER.debug("", response)

        return True

    def get_params(self, key_string=False):
        """Получить параметры с панели."""
        params = {}
        for key, value in self.__dict__.items():
            if "param_" == key[:6]:
                key = key.replace("param_", "")
                if key_string:
                    params.update({key: value.get_key_string()})
                else:
                    params.update({key: value.get_params(False)})

        return params

    def __str__(self):
        return "UserCapabilitiesModule"

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
            self.__dict__["param_" + key] = Capabilities(capabilities_params=value)
            LOGGER.debug("Param %s set to %s.", key, value)
        return True
