#!/usr/bin/python
# coding=utf8
from .general.module import BewardIntercomModule, BewardIntercomModuleError

"""
Syntax:
http://<server ipaddr>/cgi-bin/osdposition_cgi?<parameter>=<value>
[&<parameter>=<value>]
with the following parameters and values.
<parameter>=
<value>
Values Description
action=<string
>
Up, Down,
Right, Left.
The command to control the position of the
OSD.
Move 8 pixels once.
channel=<int> 0~3 The channel number of the video.
value=<int> 1,2 1: mean change the date, time, bitrate, week
position.
2: mean change the title position.
user=<string> A user name Valid characters are a thru z, A
thru Z and 0 thru 9.
pwd=<string> A user password Valid characters are a thru z, A
thru Z and 0 thru 9.
Example: Move right the title position of the channel 1.
http://192.168.88.187/cgi-bin/osdposition_cgi?channel=1&action=Right&value=2
&user=admin&pwd=admin
Response:
HTTP/1.0 200 OK\r\n
Content-Type:text/plain\r\n
\r\n
OK\r
"""


class OsdPositionModule(BewardIntercomModule):
    """Модуль взаимодействия с cgi osd position."""

    def __init__(
        self,
        client=None,
        ip=None,
        login=None,
        password=None,
        cgi="cgi-bin/osdposition_cgi",
    ):
        super(OsdPositionModule, self).__init__(client, ip, login, password, cgi)

    def load_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def update_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def set_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def get_params(self):
        raise BewardIntercomModuleError("Not implement in restart_cgi")

    def _move(self, direction, channel, value):
        """Метод для перемещения полей OSD. Поля перемещается на 8 пикселей.

        Args:
            direction(Literal['Up', 'Down', 'Right', 'Left']):
                направление перемещения.
            channel(Literal['0', '1', '2', '3']): видеоканал
            value(Literal['1', '2']):
                1 - для изменения позиции даты/скорости кадров.
                2 - для изменения позиции названия.
        """

        params = {"action": direction, "channel": channel, "value": value}
        response = self.client.query(setting=self.cgi, params=params)
        response = self.client.parse_response(response)

        if response.get("code") != 200:
            return False

        return True

    def change_position(self, *args, **kwargs):
        """Метод изменения позиции текстового поля OSD.

        Kwargs:
            lable_type(Leteral['1', '2']):
                1: для изменения позиции даты/скорости кадров.
                2: для изменения позиции названия.
            direction(Literal['Up', 'Down', 'Right', 'Left']):
                Up: перемещения поля вверх.
                Down: перемещения поля вниз.
                Right: перемещения поля вправо.
                Left: перемещения поля влево.
            channel(Literal['0', '1', '2', '3']): видеоканал [0,1,2,3].
            shift_amount(int): величина перемещения в пикселях.
        """

        lable_type, direction, channel, shift_amount = (
            kwargs.get("lable_type"),
            kwargs.get("direction"),
            kwargs.get("channel"),
            kwargs.get("shift_amount"),
        )

        PX_SHIFT = 8.0
        direction = str(direction).title()
        lable_type_check = str(lable_type) in ["1", "2"]
        direction_check = str(direction) in ["Up", "Down", "Right", "Left"]
        channel_check = str(channel) in ["0", "1", "2", "3"]
        try:
            shift_amount = float(shift_amount)
            shift_amount_check = True
        except ValueError:
            shift_amount_check = False

        if not all(
            [lable_type_check, direction_check, channel_check, shift_amount_check],
        ):
            print(lable_type_check, direction_check, channel_check, shift_amount_check)
            raise BewardIntercomModuleError("Arguments is invalid!")

        shift_count = int(round(shift_amount / PX_SHIFT, 0))
        attempts_repeat = 0

        for _ in range(shift_count):
            attempts_repeat += int(not self._move(direction, channel, lable_type))

        while attempts_repeat > 0:
            attempts_repeat -= 1
            attempts_repeat += int(not self._move(direction, channel, lable_type))

            if attempts_repeat > 500:
                return {"Message": "Error."}

        return {"Message": "Position is changed."}
