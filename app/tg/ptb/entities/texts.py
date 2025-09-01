from app.entities.match.texts import USE_GET_STATS_WITH_CMD

from .mix import texts as mix_texts
from .post import texts as post_texts
from .collection import texts as collection_texts
from .match import texts as match_texts
from .user import texts as user_texts
from .cjm import texts as cjm_texts

# Format here or in match texts?
USE_GET_STATS_WITH_CMD = USE_GET_STATS_WITH_CMD.format(GET_STATS_WITH_CMD=match_texts.Cmds.GET_STATISTIC_WITH, )
PUBLIC_COMMANDS = (
    f'{cjm_texts.CMD_DESCRIPTIONS.START}'
    f'{cjm_texts.CMD_DESCRIPTIONS.PUBLIC_MODE}'
    f'{cjm_texts.CMD_DESCRIPTIONS.PERSONAL_MODE}'
    f'{match_texts.Search.CMD_DESCRIPTIONS.SEARCH}'
    f'{user_texts.Reg.CMD_DESCRIPTIONS.REG}'
    f'{mix_texts.CMD_DESCRIPTIONS.FAQ}'
    f'{match_texts.Search.CMD_DESCRIPTIONS.PERSONAL_EXAMPLE}'
    f'{post_texts.Posts.Public.CMD_DESCRIPTIONS.CREATE_PUBLIC_POST}'
    f'{post_texts.Posts.Personal.CMD_DESCRIPTIONS.CREATE_PERSONAL_POST}'
    f'{collection_texts.Collections.CMD_DESCRIPTIONS.GET_MY_COLLECTIONS}'
    f'{match_texts.Search.CMD_DESCRIPTIONS.GET_STATISTIC_WITH}'
    f'{mix_texts.CMD_DESCRIPTIONS.GET_BOT_ALL_COMMANDS}'
)
