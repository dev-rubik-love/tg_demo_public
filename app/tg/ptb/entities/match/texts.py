from __future__ import annotations
from types import SimpleNamespace

from app.entities.match import texts
from app.entities.shared.texts import CmdDescriptions


from .constants import Cmds
from ..shared.texts import Words as SharedWords, FOR_READY
from ..post.constants import Cmds as PostCmds
from ..cjm.constants import Cmds as CjmCMds
from ..post.constants import PostsChannels


class Search(texts.Search, ):
    NO_VOTES = texts.Search.NO_VOTES.format(
        POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value,
        PUBLIC_MODE_CMD=CjmCMds.PUBLIC_MODE,
        GET_PUBLIC_POST_CMD=PostCmds.GET_PUBLIC_POST,
    )
    NO_COVOTES = texts.Search.NO_COVOTES.format(
        POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value,
        PUBLIC_MODE_CMD=CjmCMds.PUBLIC_MODE,
        GET_PUBLIC_POST_CMD=PostCmds.GET_PUBLIC_POST,
    )

    COMPLETE_KEYWORD = SharedWords.COMPLETE
    GOODBYE_KEYWORD = SharedWords.GOODBYE
    COMPLETED_KEYWORD = SharedWords.COMPLETED
    FINISH_KEYWORD = SharedWords.FINISH
    CANCEL_KEYWORD = SharedWords.CANCEL
    READY_KEYWORD = SharedWords.READY

    FOR_READY = FOR_READY

    TOTAL_LIKES_SET = texts.Search.Profile.TOTAL_LIKES_SET
    FROM = SharedWords.FROM
    TOTAL_DISLIKES_SET = texts.Search.Profile.TOTAL_DISLIKES_SET
    TOTAL_UNMARKED_POSTS = texts.Search.Profile.TOTAL_UNMARKED_POSTS
    SHARED_LIKES_PERCENTAGE = texts.Search.Profile.SHARED_LIKES_PERCENTAGE
    SHARED_DISLIKES_PERCENTAGE = texts.Search.Profile.SHARED_DISLIKES_PERCENTAGE
    SHARED_UNMARKED_POSTS_PERCENTAGE = texts.Search.Profile.SHARED_UNMARKED_POSTS_PERCENTAGE

    CMD_DESCRIPTIONS = SimpleNamespace(
        SEARCH=f'{Cmds.SEARCH} - {CmdDescriptions.SEARCH}\n',
        PERSONAL_EXAMPLE=f'{Cmds.PERSONAL_EXAMPLE} - {CmdDescriptions.SHOW_SAMPLE}\n',
        GET_STATISTIC_WITH=f'{Cmds.GET_STATISTIC_WITH} - {CmdDescriptions.GET_STAT}\n',
    )
