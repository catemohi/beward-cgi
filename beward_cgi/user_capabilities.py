#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


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
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value

    def __str__(self):
        return "UserCapabilitiesModule"
