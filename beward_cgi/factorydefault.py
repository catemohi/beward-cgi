from .general.module import BewardIntercomModule, BewardIntercomModuleError


class FactoryDefaultModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi factorydefault_cgi"""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/factorydefault_cgi",
    ):
        super(FactoryDefaultModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        raise BewardIntercomModuleError("Not implement in factorydefault_cgi")

    def update_params(self):
        raise BewardIntercomModuleError("Not implement in factorydefault_cgi")

    def set_params(self):
        raise BewardIntercomModuleError("Not implement in factorydefault_cgi")

    def get_params(self):
        raise BewardIntercomModuleError("Not implement in factorydefault_cgi")

    def reset(self):
        """Запрос сброса настроек с сохранением сети и настроек квартир."""

        response = self.client.query(setting=self.cgi)
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response

    def hard_reset(self):
        """Запрос сброса настроек с сохранением сети и настроек квартир."""

        response = self.client.query(setting="cgi-bin/hardfactorydefault_cgi")
        response = self.client.parse_response(response)
        content = response.get("content", {})

        if response.get("code") != 200:
            raise BewardIntercomModuleError(content.get("message", "Unknown error."))
        return response
