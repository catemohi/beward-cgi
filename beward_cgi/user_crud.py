#!/usr/bin/python
# coding=utf8
# from logging import getLogger

# from .general.module import BewardIntercomModule, BewardIntercomModuleError

# LOGGER = getLogger(__name__)


# class UserCrudModule(BewardIntercomModule):
#     """Модуль взаимодействия с cgi pwdgrp_cgi с учетными данными."""

#     def __init__(
#         self,
#         client=None,
#         ip=None,
#         login=None,
#         password=None,
#         cgi="cgi-bin/pwdgrp_cgi",
#     ):
#         super(UserCrudModule, self).__init__(client, ip, login, password, cgi)

#     def load_params(self):
#         """Метод получения параметров установленных на панели."""
#         content = get_all_credentials(self.client.ip)

#         for key, value in content.items():
#             if key == "message":
#                 continue

#             self.__dict__["param_" + str(key)] = value

#     def update_params(self, *args, **kwargs):
#         """Обновление параметров модуля."""
#         output = {}
#         for key, value in kwargs.items():
#             # item = self.__dict__.get("param_" + key, None)

#             params = {"action": "update", "username": key, "password": value}
#             response = self.client.query(setting=self.cgi, params=params)

#             if response.status_code == 200:
#                 self.__dict__["param_" + key] = value
#             else:
#                 LOGGER.error("Credentials for {} not updated.".format(key))

#             response = self.client.parse_response(response)
#             output[key] = response

#         return output

#     def set_params(self):
#         raise BewardIntercomModuleError("Not implement in pwdgrp_cgi for CRUD.")
#   def __str__(self):
#       return "UserCapabilitiesModule"
