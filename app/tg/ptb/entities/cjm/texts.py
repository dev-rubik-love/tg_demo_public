from __future__ import annotations
from types import SimpleNamespace

from app.entities.shared import texts as shared_texts
from app.entities.mix import texts as mix_texts

from .constants import Cmds
from ..post.constants import PostsChannels

PUBLIC_MODE = mix_texts.PUBLIC_MODE.format(POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value, )
PERSONAL_MODE = mix_texts.PERSONAL_MODE.format()

START_MODE = mix_texts.START_MODE.format(
    PUBLIC_MODE_CMD=Cmds.PUBLIC_MODE,
    PERSONAL_MODE_CMD=Cmds.PERSONAL_MODE,
)

CMD_DESCRIPTIONS = SimpleNamespace(
    START=f'{Cmds.START} - {shared_texts.CmdDescriptions.START}\n',
    PUBLIC_MODE=f'{Cmds.PUBLIC_MODE} - {shared_texts.CmdDescriptions.PUBLIC_MODE}\n',
    PERSONAL_MODE=f'{Cmds.PERSONAL_MODE} - {shared_texts.CmdDescriptions.PERSONAL_MODE}\n',
)

FOR_READY = shared_texts.FOR_READY  # CJM has no app texts, only ptb
