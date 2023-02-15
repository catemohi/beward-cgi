#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


class DateModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi date_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/date_cgi",
    ):
        super(DateModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(setting=self.cgi, params={"action": "get"})

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        message = content.get("message", None)

        if message is None:
            raise BewardIntercomModuleError("Unknown parse error.")

        message = message.replace(",", "").split()
        names = ["month", "day", "year", "time", "timezone", "ntpHost"]
        message = dict(zip(names, message))
        time = dict(zip(["hour", "minute", "second"], message.pop("time").split(":")))
        content = dict(time.items() + message.items())

        for key, value in content.items():
            if key == "message":
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value
