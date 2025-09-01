from __future__ import annotations
from types import SimpleNamespace
from typing import TYPE_CHECKING

from app.entities.shared.texts import CmdDescriptions
from app.entities.collection.texts import Collections as CollectionsTexts

from .model import Collection as CollectionModel
from .constants import Cmds
from ..post.constants import Cmds as PostsCmds
from ..match.constants import Cmds as MatchCmds
from ..shared.texts import Words as SharedWords

if TYPE_CHECKING:
    pass


class Collections(CollectionsTexts, ):

    CMD_DESCRIPTIONS = SimpleNamespace(
        GET_MY_COLLECTIONS=f'{Cmds.GET_MY_COLLECTIONS} - {CmdDescriptions.GET_COLLECTIONS}\n',
    )
    MAX_NAME_LEN = CollectionsTexts.MAX_NAME_LEN.format(MAX_NAME_LEN=CollectionModel.MAX_NAME_LEN, )
    NO_COLLECTIONS = CollectionsTexts.NO_COLLECTIONS.format(
        CREATE_PERSONAL_POST_CMD=PostsCmds.CREATE_PERSONAL_POST,
    )
    USER_ACCEPTED_SHARE_PROPOSAL = CollectionsTexts.USER_ACCEPTED_SHARE_PROPOSAL
    HERE_SHARED = CollectionsTexts.HERE_SHARED.format(
        GET_STATS_WITH_CMD=MatchCmds.GET_STATISTIC_WITH,
    )

    class Buttons:
        ACCEPT = SharedWords.ACCEPT
        DECLINE = SharedWords.DECLINE
        HIDE = SharedWords.HIDE
