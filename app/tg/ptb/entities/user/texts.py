from __future__ import annotations
from types import SimpleNamespace

from app.entities.shared.texts import MORE_ACTIONS, CmdDescriptions as AppCmdDescriptions
from app.entities.user.texts import Reg as RegTexts

from .constants import Cmds
from ..shared.texts import Words as SharedWords, Warn as SharedWarn
from .model import User


class Reg(RegTexts, ):
    TOO_MANY_PHOTOS = RegTexts.TOO_MANY_PHOTOS.format(MAX_PHOTOS=User.MAX_PHOTOS_COUNT, )  # format(USED_PHOTOS, )
    COMMAND_FOR_REG = RegTexts.COMMAND_FOR_REG.format(REG_CMD=Cmds.REG, )

    CANCEL_KEYWORD = SharedWords.CANCEL.capitalize()
    SEND_KEYWORD = SharedWords.SEND.capitalize()
    SKIP_KEYWORD = SharedWords.SKIP.capitalize()
    FINISH_KEYWORD = SharedWords.FINISH.capitalize()
    INCORRECT_FINISH = SharedWarn.INCORRECT_FINISH

    MORE_ACTIONS = MORE_ACTIONS

    CMD_DESCRIPTIONS = SimpleNamespace(
        REG=f'{Cmds.REG} - {AppCmdDescriptions.REG}\n',
    )

    OK = SharedWords.OK
