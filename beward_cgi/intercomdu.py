#!/usr/bin/python
# coding=utf8
from logging import getLogger

from .general.module import BewardIntercomModule, BewardIntercomModuleError

LOGGER = getLogger(__name__)


class IntercomduModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi intercomdu_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/intercomdu_cgi",
    ):
        super(IntercomduModule, self).__init__(
            client,
            ip,
            login,
            password,
            cgi,
        )

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        table_index = self._get_table_index()
        dozens = self._get_table_dozens()
        units = self._get_table_units()
        kkm_matrix = []
        for i in range(table_index):
            index = []
            for d in range(dozens):
                dozen = []
                for u in range(units):
                    response = self.client.query(
                        setting=self.cgi,
                        params={
                            "action": "get",
                            "Index": str(i),
                            "Dozens": str(d),
                            "Units": str(u),
                        },
                    )
                    response = self.client.parse_response(response)
                    content = response.get("content").get("message")
                    dozen.append(content)
                index.append(dozen)
            kkm_matrix.append(index)
        self.__dict__["Matrix"] = kkm_matrix
        self.__dict__["Type"] = self._get_kkm_type()

    def _get_table_index(self):
        """Получить индекс таблиц"""
        code = 200
        index = -1
        while code == 200:
            index += 1
            response = self.client.query(
                setting=self.cgi,
                params={
                    "action": "get",
                    "Index": str(index),
                },
            )
            response = self.client.parse_response(response)
            code = response.get("code")
        return index - 1

    def _get_table_dozens(self):
        """Получить количество десятков таблицы"""
        code = 200
        dozens = -1
        while code == 200:
            dozens += 1
            response = self.client.query(
                setting=self.cgi,
                params={
                    "action": "get",
                    "Index": "0",
                    "Dozens": str(dozens),
                },
            )
            response = self.client.parse_response(response)
            code = response.get("code")
        return dozens - 1

    def _get_table_units(self):
        """Получить количество едениц в десяке"""
        code = 200
        units = -1
        while code == 200:
            units += 1
            response = self.client.query(
                setting=self.cgi,
                params={
                    "action": "get",
                    "Index": "0",
                    "Dozens": "0",
                    "Units": str(units),
                },
            )
            response = self.client.parse_response(response)
            code = response.get("code")
        return units - 1

    def _get_kkm_type(self):
        """Получить тип комутатора"""
        response = self.client.query(setting=self.cgi, params={"action": "list"})

        response = self.client.parse_response(response)
        content = response.get("content", {})
        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return content["Type"]

    def set_params(self):
        """Метод загрузки параметров на панель панели."""

        params = self.get_params()
        matrix = params.pop("Matrix")
        params["action"] = "fill"
        response = self.client.query(setting=self.cgi, params=params)
        if response.status_code != 200:
            raise BewardIntercomModuleError("Error, %s" % response.status_code)
        LOGGER.debug("", response)
        for index in matrix:
            for dozen in index:
                for unit in dozen:
                    if unit == "0":
                        continue
                    params = {
                        "action": "set",
                        "Index": str(index),
                        "Dozens": str(dozen),
                        "Units": str(unit),
                    }
                    response = self.client.query(
                        setting=self.cgi,
                        params=params,
                    )
                    if response.status_code != 200:
                        LOGGER.debug("", response)
        return True
