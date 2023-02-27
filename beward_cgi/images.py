#!/usr/bin/python
# coding=utf8
from time import time

from .general.module import BewardIntercomModule, BewardIntercomModuleError


class ImagesModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi images_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/images_cgi",
    ):
        super(ImagesModule, self).__init__(client, ip, login, password, cgi)

    def __str__(self):
        return "ImagesModule"

    def load_params(self):
        raise BewardIntercomModuleError("Not implement in images_cgi")

    def update_params(self):
        raise BewardIntercomModuleError("Not implement in images_cgi")

    def set_params(self):
        raise BewardIntercomModuleError("Not implement in images_cgi")

    def get_params(self):
        raise BewardIntercomModuleError("Not implement in images_cgi")

    def get_images(self, channel, save=True, format="jpeg", save_path="."):
        """Получение изображения домфонной панели."""

        params = {"channel": channel}
        response = self.client.query(setting=self.cgi, params=params)

        if response.status_code != 200:
            content = self.client.parse_response(response).get("content", {})
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        if save:
            name = "{}\\snapshot{}.{}".format(save_path, int(time()), format)
            with open(name, "wb") as file:
                file.write(response.content)
            return True

        return response.content
