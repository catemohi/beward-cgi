#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .client import BewardClient
from .dump_creator import JSONDumpFormatter, make_dumps

LOGGER = getLogger(__name__)


class BewardIntercomModuleError(Exception):
    pass


class BewardIntercomModule(object):
    """Модуль описывающий архитектуру любого модуля для взаимодействия
    с cgi api.
    """

    def __init__(self, client=None, ip=None, login=None, password=None, cgi=""):
        """Инициализация параметров модуля."""

        if client is None:
            if login is None or password is None:
                raise BewardIntercomModuleError("Invalid credentials.")
            self.login = login
            self.password = password
            self.client = BewardClient(ip, self.login, self.password)
        else:
            self.client = client

        self.cgi = cgi

    def __str__(self):
        """Название модуля."""
        return "BewardIntercomModule"

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(setting=self.cgi, params={"action": "get"})

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"]),
            )
        for key, value in content.items():
            if "is not defined" in key or "is not defined" in value:
                raise BewardIntercomModuleError("Module is not defined")

            if "message" in key:
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value

    def update_params(self, update=None, *args, **kwargs):
        """Обновление параметров модуля.
        Args:
            update: параметры для обновления.
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

            self.__dict__["param_" + key] = value

        return True

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        params = self.get_params()
        params["action"] = "set"
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            raise BewardIntercomModuleError("Error, %s" % response.status_code)

        LOGGER.debug("", response)
        return True

    def get_params(self):
        """Получить параметры с панели."""
        params = {}
        for key, value in self.__dict__.items():
            if "param_" == key[:6]:
                key = key.replace("param_", "")
                params.update({key: value})

        return params

    def get_dump(self, formatter=JSONDumpFormatter, raw=False):
        """Сохранение параметров модуля.
        Args:
            formatter(DumpFormatter): форматирование сохранения.
            raw(bool): Получить обьект как dict
        """
        config = {self.__str__(): self.get_params()}
        if raw:
            return config
        dump_config = make_dumps(config, formatter)
        return dump_config

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
        return True
