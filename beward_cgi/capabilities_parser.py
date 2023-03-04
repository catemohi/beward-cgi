#!/usr/bin/python
# coding=utf8


"""Модуль содержащий класс хранения прав
"""

CAPABILITIES_PATTERNS = {
    32: [
        "View",
        "Door",
        "Audio",
        "Video",
        "Network",
        "Sip",
        "Record",
        "Alert",
        "Kkm",
        "ApartmentLinelevel",
        "ChangeLinelevel",
        "ServiceTime",
        "ConciergeApartment",
        "Doorcode",
        "Eeprom",
        "IntercomAlert",
        "Apartment",
        "ApartmentCodes",
        "Keys",
        "Display",
        "Gate",
        "Notifications",
        "Rtsp",
        "Onvif",
        "SystemInformation",
        "SystemTime",
        "SystemUsers",
        "SystemUpdate",
        "SystemReset",
        "SystemReboot",
        "SystemLog",
        "SystemRemoteLog",
    ],
    25: [
        "View",
        "Door",
        "Audio",
        "Video",
        "Network",
        "Sip",
        "Record",
        "Alert",
        "Kkm",
        "ApartmentLinelevel",
        "ChangeLinelevel",
        "ServiceTime",
        "ConciergeApartment",
        "Doorcode",
        "Eeprom",
        "IntercomAlert",
        "Apartment",
        "ApartmentCodes",
        "Keys",
        "Display",
        "Gate",
        "System",
        "Notifications",
        "Rtsp",
        "Onvif",
    ],
    24: [
        "View",
        "Door",
        "Audio",
        "Video",
        "Network",
        "Sip",
        "Record",
        "Alert",
        "Kkm",
        "ApartmentLinelevel",
        "ChangeLinelevel",
        "ServiceTime",
        "ConciergeApartment",
        "Doorcode",
        "Eeprom",
        "IntercomAlert",
        "Apartment",
        "ApartmentCodes",
        "Keys",
        "Display",
        "Gate",
        "System",
        "Notifications",
        "Rtsp",
    ],
    "Localization": {
        "View": "Просмотр",
        "Door": "Открытие, закрытие двери",
        "Audio": "Аудио - Настройки",
        "Video": "Видео - Все пункты управления",
        "Network": "Сеть - Все пункты управления",
        "Sip": "SIP - Все пункты управления",
        "Record": "Запись - Все пункты управления",
        "Alert": "Тревога - Все пункты управления",
        "Kkm": "Домофон - Адресация ККМ",
        "ApartmentLinelevel": "Домофон - Настройки - Уровень линии в квартире",
        "ChangeLinelevel": "Домофон - Настройки - Изменение уровней снятия трубки, открытия двери",
        "ServiceTime": "Домофон - Настройки - Время открытия двери, вызова, разговора",
        "ConciergeApartment": "Домофон - Настройки - Квартира консьержа",
        "Doorcode": "Домофон - Настройки - Сервисный код открытия двери",
        "Eeprom": "Домофон - Настройки - EEPROM, Обновление ПО микроконтроллера",
        "IntercomAlert": "Домофон - Тревога",
        "Apartment": "Домофон - Квартиры - все пункты, кроме кодов",
        "ApartmentCodes": "Домофон - Квартиры - изменение кода открытия двери, код регистрации RFID",
        "Keys": "Домофон - RFID ключи",
        "Display": "Домофон - Дисплей",
        "Gate": "Домофон - Калитка",
        "Notifications": "Оповещение",
        "Rtsp": "RTSP",
        "Onvif": "Onvif - События",
        "SystemInformation": "Системные - Информация",
        "SystemTime": "Системные - Дата и время",
        "SystemUsers": "Системные - Пользователи",
        "SystemUpdate": "Системные - Обновление",
        "SystemReset": "Системные - Сброс настроек",
        "SystemReboot": "Системные - Перезагрузка",
        "SystemLog": "Системные - Системный журнал",
        "SystemRemoteLog": "Системные - Remote syslog",
    },
}


class Capabilities(object):
    """Класс хранения прав"""

    def __init__(self, capabilities_string=None, capabilities_params=None):
        """Инициализация обьекта ключа

        Args:
            capabilities_string (str): права в строке
            capabilities_params (dict): права в словаре
        """
        if capabilities_string is None and capabilities_params is None:
            raise ValueError("Need capabilities_string or capabilities_params")
        if capabilities_string is not None:
            self._initializations_capabilities(capabilities_string)
        else:
            self.load_capabilities_from_params(capabilities_params)

    def __str__(self):
        """Отображение прав в строку"""
        return self.get_key_string()

    def __repr__(self):
        return "Capabilities({})".format(self.get_key_string())

    def _initializations_capabilities(self, capabilities_string):
        """Инициализация атрибутов прав. При инициализации ожидает строку с правами

        Args:
            capabilities_string (str): ключ и параметры ключа в строке
        """
        if not isinstance(capabilities_string, str):
            raise TypeError("Is not string")
        capabilities_params = capabilities_string.split(",")
        capabilities_pattern = CAPABILITIES_PATTERNS.get(len(capabilities_params), None)
        if capabilities_pattern is None:
            raise ValueError("Pattern not found")
        capabilities_params = dict(zip(capabilities_pattern, capabilities_params))
        for k, v in capabilities_params.items():
            self.__dict__["param_" + k] = v

    def get_params(self, localization=True):
        """Получить параметры прав."""
        params = {}
        for key, value in self.__dict__.items():
            if "param_" == key[:6]:
                key = key.replace("param_", "")
                if localization:
                    key = CAPABILITIES_PATTERNS["Localization"].get(key, key)
                params.update({key: value})
        return params

    def get_key_string(self):
        return ""


if __name__ == "__main__":
    c = Capabilities("1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1")
    print(c.get_params(localization=True))
