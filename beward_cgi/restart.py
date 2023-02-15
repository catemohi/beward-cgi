#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


class RestartModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi restart_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/restart_cgi",
    ):
        super(RestartModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def update_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def set_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def get_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def restart(self):
        """Перезагрузка домофона."""

        response = self.client.query(setting=self.cgi)
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response
