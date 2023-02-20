#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule


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
        print(table_index, dozens, units)

    def _get_table_index(self):
        """Получить индекс таблиц"""
        code = 200
        index = 0
        while code == 200:
            response = self.client.query(
                setting=self.cgi,
                params={
                    "action": "get",
                    "Index": str(index),
                },
            )
            response = self.client.parse_response(response)
            code = response.get("code")
            index += 1
        return index

    def _get_table_dozens(self):
        """Получить количество десятков таблицы"""
        code = 200
        dozens = 0
        while code == 200:
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
            dozens += 1
        return dozens

    def _get_table_units(self):
        """Получить количество едениц в десяке"""
        code = 200
        units = 0
        while code == 200:
            response = self.client.query(
                setting=self.cgi,
                params={
                    "action": "get",
                    "Index": "0",
                    "Dozens": str(units),
                },
            )
            response = self.client.parse_response(response)
            code = response.get("code")
            units += 1
        return units
