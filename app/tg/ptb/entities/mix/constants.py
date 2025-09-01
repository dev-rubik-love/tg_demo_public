# Copyright (C) 2023 David Shiko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
from re import compile as re_compile

from ..shared.constants import HIDE_S, EMPTY_CBK_S

if TYPE_CHECKING:
    pass

GEN_BOTS_S = 'gen_bots'
GEN_ME_S = 'gen_me'
ALL_BOT_COMMANDS_S = 'all_commands'
FAQ_S = 'faq'
PICKLE_FLUSH_S = 'pickle_flush'
HEALTH_S = 'health'
DONATE_S = 'donate'


class Cbks:
    EMPTY = EMPTY_CBK_S
    # (\s\d+)+ - Group (brackets ()) of space (/s) and number (\d+) repeated once or more (last "+")
    HIDE_R = re_compile(fr'^{HIDE_S}(\s\d+)+$', )


class Cmds(str, Enum):
    PICKLE_FLUSH = f'/{PICKLE_FLUSH_S}'
    FAQ = f'/{FAQ_S}'
    HEALTH = f'/{HEALTH_S}'
    GEN_BOTS = f'/{GEN_BOTS_S}'
    GEN_ME = f'/{GEN_ME_S}'
    GET_BOT_ALL_COMMANDS = f'/{ALL_BOT_COMMANDS_S}'
