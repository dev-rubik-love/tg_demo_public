from __future__ import annotations
from re import compile as re_compile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

PUBLIC_VOTE_S = 'public_vote'
CHANNEL_PUBLIC_VOTE_S = 'channel_public_vote'
PERSONAL_VOTE_S = 'personal_vote'


class Cbks:
    PUBLIC_VOTE = PUBLIC_VOTE_S
    CHANNEL_PUBLIC_VOTE = CHANNEL_PUBLIC_VOTE_S
    PERSONAL_VOTE = PERSONAL_VOTE_S
    # ^ - exactly starts with
    # $ - exactly ends with
    # \d+ - Any count of digits. just \d is only single digit
    PUBLIC_VOTE_R = re_compile(fr'^{PUBLIC_VOTE_S}', )
    CHANNEL_PUBLIC_VOTE_R = re_compile(fr'^{CHANNEL_PUBLIC_VOTE_S}', )
    PERSONAL_VOTE_R = re_compile(fr'^{PERSONAL_VOTE_S}', )
