#!/usr/bin/python
# coding=utf8
import json


class DumpLoader:

    """Интерфейс для любых классов загрузки конфигураций.

    Attributes:
        DUMP: загруженый конфиг.
    """

    DUMP = str

    @classmethod
    def loads(cls, config):

        """Метод, который вызывается для загрузки конфигурации.

        Args:
            config (dict): сырой конфиг

        Raises:
            NotImplementedError: не реализован.

        Returns:
            DUMP: форматированный ответ.
        """
        raise NotImplementedError

    @classmethod
    def load(cls, file):

        """Метод, который вызывается для загрузки конфигурации.

        Args:
            config (bytes): открытый файл конфигурации.

        Raises:
            NotImplementedError: не реализован.

        Returns:
            DUMP: форматированный ответ.
        """
        raise NotImplementedError


class JSONDumpLoader(DumpLoader):

    """Класс для создание конфигов в формате JSON"""

    DUMP = dict

    @classmethod
    def loads(cls, config):

        """Метод для загрузки конфигурации.

        Args:
            config: сырой конфига, который требуется загрузить.

        Returns:
            DUMP: загруженная конфигурация.

        """
        return json.loads(config)

    @classmethod
    def load(cls, file):

        """Метод для загрузки конфигурации.

        Args:
            config: сырой конфига, который требуется отформатировать.

        Returns:
            DUMP: загруженная конфигурация.

        """
        return json.load(file)


def load_dump(file, loader):

    """Функция загрузки конфигурации из файла.

    Args:
        file: файл конфигурации.
        loader: класс для загрузки конфигурации

    Returns:
        DumpLoader.DUMP: конфиг.
    Raises:

    """

    return loader.load(file)


def loads_dump(config, loader):

    """Функция форматорования конфигурации.

    Args:
        config: сырой конфиг
        loader: класс для загрузки конфигурации

    Returns:
        DumpLoader.DUMP: конфиг.

    Raises:

    """

    return loader.loads(config)
