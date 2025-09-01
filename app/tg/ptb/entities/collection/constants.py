from __future__ import annotations
from enum import Enum
from re import compile as re_compile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

GET_MY_COLLECTIONS_S = 'get_my_collections'
GET_DEFAULT_COLLECTIONS_S = 'get_default_collections'  # Not in use
CREATE_COLLECTION_S = 'create_collection'
SHARE_COLLECTIONS_S = 'share_collections'


class Cbks:
    # Especially for personal mode posts sharing cuz posts cbk handler for public and personal mode are different
    SHOW_COLLECTION_POSTS = 'show_collection_posts'
    SHOW_SHARED_COLLECTION_POSTS = 'show_shared_collection_posts'
    MARK_COLLECTION = 'mark_collection'
    GET_MY_COLLECTIONS_WITH_PERSONAL_POSTS_S = 'get_my_collections_with_personal_posts'
    ACCEPT_COLLECTIONS = 'accept_collections'
    MARK_COLLECTION_AND_SHOW_POSTS = 'mark_show_collection'
    CHOOSE_COLLECTION = 'choose_collection'

    # Especially for personal mode posts sharing cuz posts cbk handler for public and personal mode are different
    SHOW_COLLECTION_POSTS_R = re_compile(fr'^{SHOW_COLLECTION_POSTS} \d+$', )
    # Second digit is sender id
    SHOW_SHARED_COLLECTION_POSTS_R = re_compile(fr'^{SHOW_SHARED_COLLECTION_POSTS} \d+ \d+$', )
    MARK_COLLECTION_R = re_compile(fr'^{MARK_COLLECTION} \d+$')  # text that ending with digits
    ACCEPT_COLLECTIONS_R = re_compile(fr'^{ACCEPT_COLLECTIONS}', )
    # CHOOSE_COLLECTION_R = fr'{CHOOSE_COLLECTION}( \d+)*'  # ( \d+)* - number with leading space any number of times
    # - collection name and bool int 01 (is_chosen)
    CHOOSE_COLLECTION_R = re_compile(fr'^{CHOOSE_COLLECTION} .* [01]$')


class Cmds(str, Enum):
    GET_DEFAULT_COLLECTIONS = f'/{GET_DEFAULT_COLLECTIONS_S}'  # Not in use
    GET_MY_COLLECTIONS = f'/{GET_MY_COLLECTIONS_S}'
    CREATE_COLLECTION = f'/{CREATE_COLLECTION_S}'
    SHARE_COLLECTIONS = f'/{SHARE_COLLECTIONS_S}'
