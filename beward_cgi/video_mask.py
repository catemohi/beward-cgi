#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


class VideoMaskModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi videomask_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/videomask_cgi",
    ):
        super(VideoMaskModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(setting=self.cgi, params={"action": "get"})
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))

        if not content:
            raise BewardIntercomModuleError("Unknown parse error.")

        for key, value in content.items():
            if "message" in key and value:
                content.pop(key)
                value = [line.split(";") for line in value.split()]
                content.update(dict(value))

        for key, value in content.items():
            if key == "message":
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value
