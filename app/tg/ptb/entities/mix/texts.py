from __future__ import annotations
from types import SimpleNamespace

from app.entities.mix import texts
from app.entities.shared.texts import CmdDescriptions
from app.config import BOT_NAME

from .constants import Cmds
from ..match.constants import Cmds as MatchCmds
from ..user.constants import Cmds as UserCmds
from ..cjm.constants import Cmds as CjmCmds

DONATE = texts.DONATE
MISUNDERSTAND = texts.MISUNDERSTAND

FAQ = texts.FAQ.format(
    BOT_NAME=BOT_NAME,
    REG_CMD=UserCmds.REG,
    PUBLIC_MODE_CMD=CjmCmds.PUBLIC_MODE,
    PERSONAL_MODE_CMD=CjmCmds.PERSONAL_MODE,
    SEARCH_CMD=MatchCmds.SEARCH,
)

CMD_DESCRIPTIONS = SimpleNamespace(
    FAQ=f'{Cmds.FAQ} - {CmdDescriptions.FAQ}\n',
    GET_BOT_ALL_COMMANDS=f'{Cmds.GET_BOT_ALL_COMMANDS} - {CmdDescriptions.BOT_USER_COMMANDS}\n',
)

CmdDescriptions = CmdDescriptions
