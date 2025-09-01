from enum import Enum
from re import compile as re_compile

SEARCH_S = 'search'
GET_STATISTIC_WITH_S = 'get_stats_with'
PERSONAL_EXAMPLE_S = 'personal_example'


class Cbks:
    CHECKBOX = 'checkboxes'
    CHOOSE_CHANNELS = 'ask_votes_channel_sources'
    CHECKBOX_R = re_compile(fr'^{CHECKBOX}', )
    # brackets to create groups for easiest future parsing (just str.split will fail cuz .* arbitrary len)
    CHOOSE_CHANNELS_R = re_compile(fr'^({CHOOSE_CHANNELS}) (.*) ([01])$', )


class Cmds(str, Enum):
    SEARCH = f'/{SEARCH_S}'
    GET_STATISTIC_WITH = f'/{GET_STATISTIC_WITH_S}'
    PERSONAL_EXAMPLE = f'/{PERSONAL_EXAMPLE_S}'
