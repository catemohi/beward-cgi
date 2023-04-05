#!/usr/bin/python
# coding=utf8
from datetime import timedelta

from .general.module import BewardIntercomModule, BewardIntercomModuleError


class DateModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi date_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/date_cgi",
    ):
        super(DateModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "DateModule"

    def load_params(self):
        """Метод получения параметров установленных на панели."""

        response = self.client.query(setting=self.cgi, params={"action": "get"})

        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        message = content.get("message", None)

        if message is None:
            raise BewardIntercomModuleError("Unknown parse error.")

        message = message.replace(",", "").split()
        names = ["month", "day", "year", "time", "timezone", "ntpHost"]
        message = dict(zip(names, message))
        time = dict(zip(["hour", "minute", "second"], message.pop("time").split(":")))
        content = dict(list(time.items()) + list(message.items()))

        for key, value in content.items():
            if key == "message":
                continue

            try:
                self.__dict__["param_" + str(key)] = str(value)
            except UnicodeEncodeError:
                self.__dict__["param_" + str(key)] = value

        self.__dict__["param_timezone"] = BewardTimeZone(
            int(self.__dict__["param_timezone"]),
        )

    def get_params(self):
        """Получить параметры с панели"""
        params =  {}
        params = super().get_params()
        params.update({"timezone": self.__dict__["param_timezone"].get_value()})
        return params

class BewardTimeZone(object):
    """Временные зоны для date_cgi"""

    _TIMEZONE = [
        {
            "offset": timedelta(hours=-12),
            "abbreviation": "BIT",
            "value": 0,
            "description": "Dateline Standard Time",
        },
        {
            "offset": timedelta(hours=-11),
            "abbreviation": "SMST",
            "value": 1,
            "description": "Samoa Standard Time",
        },
        {
            "offset": timedelta(hours=-10),
            "abbreviation": "HST",
            "value": 2,
            "description": "Hawaiian Standard Time",
        },
        {
            "offset": timedelta(hours=-9),
            "abbreviation": "AKST",
            "value": 3,
            "description": "Alaskan Standard Time",
        },
        {
            "offset": timedelta(hours=-8),
            "abbreviation": "PST",
            "value": 4,
            "description": "Pacific Standard Time",
        },
        {
            "offset": timedelta(hours=-7),
            "abbreviation": "MST",
            "value": 5,
            "description": "Mountain Standard Time",
        },
        {
            "offset": timedelta(hours=-6),
            "abbreviation": "CST",
            "value": 6,
            "description": "Monterrey Central Standard Time",
        },
        {
            "offset": timedelta(hours=-5),
            "abbreviation": "EST",
            "value": 7,
            "description": "Eastern Standard Time",
        },
        {
            "offset": timedelta(hours=-5),
            "abbreviation": "SAPST",
            "value": 8,
            "description": "SA Pacific Standard Time",
        },
        {
            "offset": timedelta(hours=-4),
            "abbreviation": "AST",
            "value": 9,
            "description": "Atlantic Standard Time",
        },
        {
            "offset": timedelta(hours=-3.5),
            "abbreviation": "NST",
            "value": 10,
            "description": "Newfoundland and Labrador Standard Time",
        },
        {
            "offset": timedelta(hours=-3),
            "abbreviation": "ART",
            "value": 11,
            "description": "Argentina Standard Time",
        },
        {
            "offset": timedelta(hours=-2),
            "abbreviation": "GST",
            "value": 12,
            "description": "Mid-Atlantic Standard Time",
        },
        {
            "offset": timedelta(hours=-1),
            "abbreviation": "CVT",
            "value": 13,
            "description": "Cabo Verde Standard Time",
        },
        {
            "offset": timedelta(hours=0),
            "abbreviation": "GMT",
            "value": 14,
            "description": "GMT Standard Time",
        },
        {
            "offset": timedelta(hours=1),
            "abbreviation": "WET",
            "value": 15,
            "description": "West Europe;Standard Time",
        },
        {
            "offset": timedelta(hours=1),
            "abbreviation": "CET",
            "value": 16,
            "description": "Central Europe Standard Time",
        },
        {
            "offset": timedelta(hours=1),
            "abbreviation": "RST",
            "value": 17,
            "description": "Romance Standard Time",
        },
        {
            "offset": timedelta(hours=1),
            "abbreviation": "ECT",
            "value": 18,
            "description": "Central Africa Standard Time",
        },
        {
            "offset": timedelta(hours=2),
            "abbreviation": "GTBST",
            "value": 19,
            "description": "GTB Standard Time",
        },
        {
            "offset": timedelta(hours=2),
            "abbreviation": "EET",
            "value": 20,
            "description": "Turkey Standard Time",
        },
        {
            "offset": timedelta(hours=3),
            "abbreviation": "MSK",
            "value": 21,
            "description": "Russian Standard Time",
        },
        {
            "offset": timedelta(hours=3.5),
            "abbreviation": "IRST",
            "value": 22,
            "description": "Iran Standard Time",
        },
        {
            "offset": timedelta(hours=4),
            "abbreviation": "AMT",
            "value": 23,
            "description": "Caucasus Standard Time",
        },
        {
            "offset": timedelta(hours=4.5),
            "abbreviation": "AFT",
            "value": 24,
            "description": "Afghanistan Standard Time",
        },
        {
            "offset": timedelta(hours=5),
            "abbreviation": "WAST",
            "value": 25,
            "description": "West Asia Standard Time",
        },
        {
            "offset": timedelta(hours=5),
            "abbreviation": "IST",
            "value": 26,
            "description": "India Standard Time",
        },
        {
            "offset": timedelta(hours=6),
            "abbreviation": "BTT",
            "value": 27,
            "description": "Central Asia Standard Time",
        },
        {
            "offset": timedelta(hours=7),
            "abbreviation": "THA",
            "value": 28,
            "description": "SE Asia Standard Time",
        },
        {
            "offset": timedelta(hours=8),
            "abbreviation": "CST",
            "value": 29,
            "description": "China Standard Time",
        },
        {
            "offset": timedelta(hours=9),
            "abbreviation": "TST",
            "value": 30,
            "description": "Tokyo Standard Time",
        },
        {
            "offset": timedelta(hours=9.5),
            "abbreviation": "ACST",
            "value": 31,
            "description": "Australia Standard Time",
        },
        {
            "offset": timedelta(hours=10),
            "abbreviation": "WPST",
            "value": 32,
            "description": "West Pacific Standard Time",
        },
        {
            "offset": timedelta(hours=11),
            "abbreviation": "SBT",
            "value": 33,
            "description": "Central Pacific Standard Time",
        },
        {
            "offset": timedelta(hours=12),
            "abbreviation": "FJT",
            "value": 34,
            "description": "Fiji Standard Time",
        },
    ]

    def __init__(self, index):
        try:
            index = int(index)
        except TypeError:
            raise TypeError("Index must be an integer or string")
        self._timezone = self._TIMEZONE[index]

    def __str__(self):
        return "BewardTimeZone.{}".format(self._timezone.get("abbreviation"))

    @property
    def timezone(self):
        """Получить временную зону"""
        return self._timezone

    def set(self, offset=None, abbreviation=None):
        """Изменение временной зоны

        Args:
            abbreviation (str): аббревиатура. Defaults to None.
            offset (timedelta): временное смещение. Defaults to None.
        """
        if all([offset is None, abbreviation is None]):
            raise ValueError("Offset or abbreviation must be specified")
        if offset is not None:
            if not isinstance(offset, timedelta):
                raise TypeError("Offset must be a timedelta")
            tz = dict([(tz["offset"], tz) for tz in self._TIMEZONE])
            tz = tz.get(offset, None)
            if tz is None:
                raise ValueError("Offset %s is not known" % offset)
            self._timezone = tz
            return (True, tz)

        tz = dict([(tz["abbreviation"], tz) for tz in self._TIMEZONE])
        tz = tz.get(abbreviation, None)
        if tz is None:
            raise ValueError("Abbreviation %s is not known" % offset)
        self._timezone = tz
        return (True, tz)

    def get(self):
        """Получить временную зону"""
        return self._timezone

    def get_value(self):
        """Получить Beward значение временной зоны"""
        return str(self.timezone["value"])
