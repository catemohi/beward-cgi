#!/usr/bin/python
# coding=utf8
from logging import getLogger
from json import loads

from .client import BewardClient


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
            if login is None:
                raise BewardIntercomModuleError("Unauthorized.")
            if self.password is None:
                raise BewardIntercomModuleError("Unauthorized.")
            self.client = BewardClient(ip, self.login, self.password)
        else:
            self.client = client

        self.cgi = cgi

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(setting=self.cgi, params={"action": "get"})

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if content["message"]:
            raise BewardIntercomModuleError(
                "Parsing error. Response: {}".format(content["message"])
            )
        for key, value in content.items():
            if "message" in key:
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value

    def update_params(self, *args, **kwargs):
        """Обновление параметров модуля."""

        for key, value in kwargs.items():
            item = self.__dict__.get("param_" + key, None)

            if item is None:
                continue

            self.__dict__["param_" + key] = value

        return self.set_params()

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        params = self.get_params()
        params["action"] = "set"
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            return {"Message": "Module params has not been changed."}

        return {"Message": "Module params is changed."}

    def get_params(self):
        """Получить параметры с панели."""
        params = {}
        for key, value in self.__dict__.items():
            if "param_" == key[:6]:
                key = key.replace("param_", "")
                params.update({key: value})

        return params
