#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


class UpgradeModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi upgrade_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/upgrade_cgi",
    ):
        super(UpgradeModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        raise BewardIntercomModuleError("Not implement in upgrade_cgi")

    def update_params(self):
        raise BewardIntercomModuleError("Not implement in upgrade_cgi")

    def set_params(self):
        raise BewardIntercomModuleError("Not implement in upgrade_cgi")

    def get_params(self):
        raise BewardIntercomModuleError("Not implement in upgrade_cgi")

    def upgrade(self, file):
        """РТП обновление прошивки домофона.

        Args:
            file: файл прошивки домофона.
        """

        params = {"action": "upgrade"}
        files = {"file": file}
        timeout = 120

        response = self.client.query_post(
            setting=self.cgi,
            params=params,
            files=files,
            timeout=timeout,
        )
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response

    def __str__(self):
        return "UpgradeModule"
