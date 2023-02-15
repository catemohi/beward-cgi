#!/usr/bin/python
# coding=utf8
from collections import OrderedDict
from logging import getLogger

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

LOGGER = getLogger(__name__)


class Client(object):
    """Класс для работы с запросами к оборудованию."""

    def __init__(self, ip=None, login=None, password=None):
        """Инициаизация клиента для связис панелью."""

        LOGGER.debug("Инициализация экземпляра класса клиента")
        self.ip = ip
        self.login = login
        self.password = password
        self.session = self.create_session()

    def create_session(self):
        LOGGER.debug("Создание сессии с  ip: {}.".format(self.ip))
        s = requests.Session()
        retry = Retry(total=5, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        s.auth = (self.login, self.password)
        return s

    def get_url(self, proto="http", setting=None):
        LOGGER.debug("Начало создания ссылки")
        url = "{protocol}://".format(protocol=proto)

        if self.ip:
            LOGGER.debug("Добавление ip-адреса :{host} к ссылке".format(host=self.ip))
            url += "{host}/".format(host=self.ip)

        if setting:
            LOGGER.debug(
                "Добавление настройки :{setting} к ссылке".format(setting=setting),
            )
            url += "{setting}".format(setting=setting)

        LOGGER.debug("Ссылка создана: {}".format(url))
        return url

    def query(self, setting=None, params=None, timeout=5, verify=False):
        url = self.get_url(setting=setting)
        LOGGER.debug("Запрос:{host}.".format(host=url))

        if params:
            LOGGER.debug("Param load: {}".format(params))
            return self.session.get(url, timeout=timeout, params=params, verify=verify)

        return self.session.get(url, timeout=timeout)

    def query_post(
        self,
        setting=None,
        params=None,
        files=None,
        timeout=5,
        verify=False,
    ):
        url = self.get_url(setting=setting)
        LOGGER.debug("Запрос:{host}.".format(host=url))

        if files:
            return self.session.post(
                url,
                timeout=timeout,
                files=files,
                params=params,
                verify=verify,
            )

        elif params:
            return self.session.post(url, timeout=timeout, params=params, verify=verify)

        return self.session.post(url, timeout=timeout)

    def close(self):
        LOGGER.debug("Сессия закрыта.")
        return self.session.close()


class BewardClient(Client):
    """Клиент для взаимодействия с домофонными панелями Beward."""

    def parse_response(self, response):
        """Парсинг ответа от домофна Beward."""

        content = response.content.decode("UTF-8").replace("\r", "").split("\n")
        content = [line for line in content if line]
        parse_content = OrderedDict()

        for number, line in enumerate(content):
            try:
                line = str(line).split("=")
            except UnicodeEncodeError:
                line = line.split("=")

            if len(line) == 2:
                parse_content[line[0]] = line[1]
            elif len(line) == 1 and len(content) == 1:
                parse_content["message"] = line[0]
            elif len(line) == 1:
                parse_content["message_{}".format(number)] = line[0]
            else:
                parse_content["message_{}".format(number)] = ";".join(line)

        if "message" not in parse_content:
            parse_content["message"] = ""

        return {
            "code": response.status_code,
            "content": parse_content,
        }
