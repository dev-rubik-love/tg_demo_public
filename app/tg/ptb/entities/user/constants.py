from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

REG_S = 'reg'


class Cmds(str, Enum):
    REG = f'/{REG_S}'
