#!/usr/bin/python
# coding=utf8
from re import findall

"""Модуль содержащий класс хранения ключа

"""


class Key(object):
    """Класс для хранения ключа
    Обьект может хранить как ключ RFID, так и MIFARE
    Атрибуты экземпляра класса:
        Key: UID ключа, дополненный при необходимости до 7 байт
        нулями (домофоном оперирует UID ключа в обратном порядке байт)
        Apartment: квартира, к которой привязан ключ
        Параметр не используется, если ключ не привязывается к квартире
        Type: тип электронного ключа/метки
            0 - Ultralight C
            1 - Mifare Classic
            2 - Mifare Plus SE
            3 - Mifare Plus X
        ProtectedMode: защищенный режим
            0 - выключен
            1 - включен
        CipherIndex: индекс шифра
            min - 1 (соответствует первому шифру в таблице)
            max - 65535
        NewCipherEnable: смена шифра для ключа
            0 - выключен
            1 - включен
        NewCipherIndex: новый индекс шифра
            min - 1 (соответствует первому шифру в таблице)
            max - 65535
        Code: код
            Формат - 4 байта в hex
            Пример - 01FFAE67
            Значение
                min - 00000001
                max - FFFFFFFF
        Sector: номер сектора
            Значение
                min - 1
                max - 9999
        Owner: владелец
        AutoPersonalize: автоперсонализация
            Значение
                0 - включена
                1 - выключена
        Service - сервисный ключ
            Значение
                0 - включена
                1 - выключена
    При инициализации ожидает строку с ключем и параметрами:
        RFID:
            Key, Apparent
        MIFARE:
            Key,Type,ProtectedMode,CipherIndex,NewCipherEnable,NewCipherIndex,
                Code,Sector,Apartment,Owner,AutoPersonalize,Service
        Можно передавать не все параметры, в таком случае надо оставлять запятые
        00000041A1D8B3,,,,,,,,,,0,0
        00000041A1D8B3,
    Распаршивает ее в атрибуты экземпляра класса
    Может вернуть ключ формате атрибутов для дальнейщего запроса:
        get_params
    Может вернуть ключ формате строки для csv:
        get_key_string
    """

    def __init__(self, key_string):
        """Инициализация обьекта ключа

        Args:
            key_string (str): ключ и параметры ключа в строке
        """
        self.mifare_pattern = (
            "Key",
            "Type",
            "ProtectedMode",
            "CipherIndex",
            "NewCipherEnable",
            "NewCipherIndex",
            "Code",
            "Sector",
            "Apartment",
            "Owner",
            "AutoPersonalize",
            "Service",
        )
        self.rfid_pattern = ("Key", "Apartment")
        self._initializations_key(key_string)

    def _initializations_key(self, key_string):
        """Инициализация атрибутов экземпляра класса.

        При инициализации ожидает строку с ключем и параметрами:

        RFID: Key, Apparent

        MIFARE: Key, Type, ProtectedMode, CipherIndex, NewCipherEnable,
            NewCipherIndex, Code, Sector, Apartment, Owner,
            AutoPersonalize, Service

        Можно передавать не все параметры, в таком случае надо оставлять запятые:
            Пример:
                MIFARE: 00000041A1D8B3,,,,,,,,,,0,0
                RFID: 00000041A1D8B3,

        Args:
            key_string (str): ключ и параметры ключа в строке
        """
        if not isinstance(key_string, str):
            raise TypeError("Is not string")
        key_pattern = r"[0-9A-F]{2,}"
        if not findall(key_pattern, key_string):
            raise ValueError("Key is not found")
        keys_and_params = key_string.split(",")
        if len(keys_and_params) == 1:
            key = {"Key": keys_and_params[0]}
            key = self._append_params(key)
        elif len(keys_and_params) == 2:
            if not keys_and_params[1]:
                keys_and_params[1] = "0"
            key = dict(zip(self.rfid_pattern, keys_and_params))
            key = self._append_params(key)
        elif len(keys_and_params) == 12:
            key = dict(zip(self.mifare_pattern, keys_and_params))
        else:
            raise ValueError("Wrong number of parameters")
        for k, v in key.items():
            self.__dict__["param_" + k] = v

    def _append_params(self, key):
        """Метод добавление несуществующих параметров ключа"""
        for param in set(self.mifare_pattern) - set(key):
            if param == "Owner":
                key[param] = ""
            elif param in ["Type", "Sector"]:
                key[param] = "1"
            else:
                key[param] = "0"
        return key

    def get_params(self, format_type="MIFARE"):
        """Получить параметры ключа."""
        params = {}
        for key, value in self.__dict__.items():
            if "param_" == key[:6]:
                key = key.replace("param_", "")
                params.update({key: value})
        if format_type == "MIFARE":
            return params
        elif format_type == "RFID":
            return {"Key": params["Key"], "Apartment": params["Apartment"]}
        return {}

    def get_key_string(self, format_type="MIFARE"):
        """Возвращает ключ в нужном формате строкой

        Args:
            format_type (str, optional): формат строки. Defaults to "MIFARE".
        """
        end_string = ""
        if format_type == "MIFARE":
            for param in self.mifare_pattern:
                end_string += self.__dict__["param_" + param] + ","
            return end_string[:-1]
        elif format_type == "RFID":
            for param in self.rfid_pattern:
                end_string += self.__dict__["param_" + param] + ","
            return end_string[:-1]
        return ""


if __name__ == "__main__":
    short_key = Key("01FFAE67")
    key = Key("00000041A1D8B3")
    rfid_key = Key("00000041A1D8B3,0")
    mifare_key = Key("00000041A1D8B3,1,0,0,0,0,0,1,0,,0,0")
    assert (
        mifare_key.get_key_string(string_type="MIFARE")
        == "00000041A1D8B3,1,0,0,0,0,0,1,0,,0,0"
    )
    assert mifare_key.get_key_string(string_type="RFID") == "00000041A1D8B3,0"
    assert short_key.get_params() == {
        "Key": "01FFAE67",
        "CipherIndex": "0",
        "Service": "0",
        "AutoPersonalize": "0",
        "Code": "0",
        "Type": "1",
        "ProtectedMode": "0",
        "Sector": "1",
        "Owner": "",
        "NewCipherIndex": "0",
        "Apartment": "0",
        "NewCipherEnable": "0",
    }
    assert key.get_params() == {
        "Key": "00000041A1D8B3",
        "CipherIndex": "0",
        "Service": "0",
        "AutoPersonalize": "0",
        "Code": "0",
        "Type": "1",
        "ProtectedMode": "0",
        "Sector": "1",
        "Owner": "",
        "NewCipherIndex": "0",
        "Apartment": "0",
        "NewCipherEnable": "0",
    }
    assert rfid_key.get_params() == {
        "Key": "00000041A1D8B3",
        "Apartment": "0",
        "CipherIndex": "0",
        "Service": "0",
        "AutoPersonalize": "0",
        "Code": "0",
        "Type": "1",
        "ProtectedMode": "0",
        "Sector": "1",
        "Owner": "",
        "NewCipherIndex": "0",
        "NewCipherEnable": "0",
    }
    assert mifare_key.get_params() == {
        "Key": "00000041A1D8B3",
        "Type": "1",
        "ProtectedMode": "0",
        "CipherIndex": "0",
        "NewCipherEnable": "0",
        "NewCipherIndex": "0",
        "Code": "0",
        "Sector": "1",
        "Apartment": "0",
        "Owner": "",
        "AutoPersonalize": "0",
        "Service": "0",
    }
    try:
        Key("")
    except ValueError as err:
        assert str(err) == "Key not found in string"
    try:
        Key(1)
    except ValueError as err:
        assert str(err) == "Is not string"
    try:
        Key([])
    except ValueError as err:
        assert str(err) == "Is not string"
