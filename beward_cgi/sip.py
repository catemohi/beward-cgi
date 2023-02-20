#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError


class SipModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi sip_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/sip_cgi",
    ):
        super(SipModule, self).__init__(client, ip, login, password, cgi)

    def get_regstatus(self):
        """Запрос получения статуса регистрации SIP."""

        params = {"action": "regstatus"}
        response = self.client.query(setting=self.cgi, params=params)
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response

    def call(self, number):
        params = {"action": "call", "Uri": number}
        response = self.client.query(setting=self.cgi, params=params)
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response
