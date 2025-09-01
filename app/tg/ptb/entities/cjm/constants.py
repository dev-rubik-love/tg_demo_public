from __future__ import annotations
from enum import Enum
from re import compile as re_compile

# noinspection PyUnresolvedReferences
from ..shared.constants import NO_SPACE_R, START_S

PERSONAL_MODE_S = 'personal_mode'
PUBLIC_MODE_S = 'public_mode'


class Cbks:
    MARK_COLLECTION_AND_SHOW_POSTS = 'mark_show_collection'
    MARK_SHOW_COLLECTION_R = re_compile(fr'^{MARK_COLLECTION_AND_SHOW_POSTS} \d+$', )  # text that ending with digits


class Cmds(str, Enum):
    START = f'/{START_S}'
    PUBLIC_MODE = f'/{PUBLIC_MODE_S}'
    PERSONAL_MODE = f'/{PERSONAL_MODE_S}'
