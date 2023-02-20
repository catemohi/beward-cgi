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
        print(kkm_matrix)

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
