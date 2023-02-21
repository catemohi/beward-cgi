#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .general.module import BewardIntercomModule, BewardIntercomModuleError

LOGGER = getLogger(__name__)


class HttpsModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi https_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/https_cgi",
    ):
        self.cert_Country = ""
        self.cert_State = ""
        self.cert_Locality = ""
        self.cert_Organization = ""
        self.cert_Unit = ""
        self.cert_CommonName = ""
        self.cert_Days = ""
        super(HttpsModule, self).__init__(client, ip, login, password, cgi)

    def delete_cert(self):
        """Запрос удаления самоподписанного сертификата HTTPS"""
        response = self.client.query(
            setting=self.cgi,
            params={
                "action": "deletecert",
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
        return True

    def delete_req(self):
        """Запрос удаления запроса сертификата HTTPS"""
        response = self.client.query(
            setting=self.cgi,
            params={
                "action": "deletereq",
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
        return True

    def get_cert_params(self):
        """Получить параметры сертификата."""
        params = {}
        for key, value in self.__dict__.items():
            if "cert_" == key[:5]:
                key = key.replace("cert_", "")
                params.update({key: value})

        return params

    def create_cert(self):
        """Создать сертификат HTTPS."""

        params = self.get_cert_params()
        params["action"] = "createcert"
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            raise BewardIntercomModuleError("Error, %s" % response.status_code)

        LOGGER.debug("", response)
        return True

    def update_cert_params(self, update=None):
        """Обновить параметры сертификата."""
        if update is None:
            update = {}
        for key, value in update.items():
            item = self.__dict__.get("cert_" + key, None)

            if item is None:
                continue

            self.__dict__["cert_" + key] = value

        return True
