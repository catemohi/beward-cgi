#!/usr/bin/python
# coding=utf8
import json
from datetime import datetime, timedelta


class DumpFormatter:

    """Интерфейс для любых классов создания конфигурации.

    Attributes:
        FORMATTED_DUMP: формат ответа.
    """

    FORMATTED_DUMP = str

    @classmethod
    def make(cls, config):

        """Метод, который вызывается для формирования отчета.

        Args:
            config (dict): сырой конфиг

        Raises:
            NotImplementedError: не реализован.

        Returns:
            FORMATTED_DUMP: форматированный ответ.
        """
        raise NotImplementedError


class JSONDumpFormatter(DumpFormatter):

    """Класс для создание конфигов в формате JSON"""

    FORMATTED_DUMP = "str"

    @classmethod
    def make(cls, config):

        """Метод для форматирования конфига.

        Args:
            config: сырой конфига, который требуется отформатировать.

        Returns:
            FORMATTED_RESPONSE: отформатированный ответ.

        """

        json_string = json.dumps(
            config,
            sort_keys=False,
            ensure_ascii=False,
            separators=(",", ": "),
            cls=EnhancedJSONEncoder,
        )
        return json_string


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, encoding_object):
        if isinstance(encoding_object, datetime):
            return datetime.strftime(encoding_object, "%d.%m.%Y %H:%M:%S")
        if isinstance(encoding_object, timedelta):
            return encoding_object.total_seconds()
        return super().default(encoding_object)


def make_dumps(config, formatter):

    """Функция форматорования конфигурации.

    Args:
        config: сырой конфиг
        formatter: класс для форматированния конфигурации

    Returns:
        DumpFormatter.FORMATTED_DUMP: форматированный конфиг.

    Raises:

    """

    return formatter.make(config)
