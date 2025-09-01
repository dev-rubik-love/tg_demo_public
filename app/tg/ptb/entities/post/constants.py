from __future__ import annotations
from enum import Enum
from re import compile as re_compile, IGNORECASE
from typing import TYPE_CHECKING

from app.config import TG_POSTS_CHANNEL, TG_POSTS_STORE, TG_POSTS_CHANNEL_LINK
from ..shared.constants import START_S, READY_R, EMPTY_CBK_S, EMPTY_CBK_R

if TYPE_CHECKING:
    pass


class PostsChannels(Enum, ):
    POSTS = TG_POSTS_CHANNEL  # Main posts source
    STORE = TG_POSTS_STORE  # Store for posts (intermediate proxy place)
    POSTS_LINK = TG_POSTS_CHANNEL_LINK  # Main posts source name


SEND_S = 'send'  # Move to shared?
POST_S = 'post'
GET_PUBLIC_POST_S = 'get_public_post'
GET_MY_PERSONAL_POSTS_S = 'get_my_personal_posts'
CREATE_PUBLIC_POST_S = 'create_public_post'
CREATE_PERSONAL_POST_S = 'create_personal_post'
SHARE_PERSONAL_POSTS_S = 'share_personal_posts'
REQUEST_PERSONAL_POSTS_S = 'request_personal_posts'


class Cbks:
    EMPTY = EMPTY_CBK_S
    ACCEPT_PERSONAL_POSTS = 'accept_personal_posts'
    REQUEST_PERSONAL_POSTS = 'request_personal_posts'
    UPDATE_PUBLIC_POST_STATUS = 'update_public_post_status'
    ACCEPT_PERSONAL_POSTS_R = re_compile(fr'^{ACCEPT_PERSONAL_POSTS}', )
    REQUEST_PERSONAL_POSTS_R = re_compile(fr'^{REQUEST_PERSONAL_POSTS}', )
    UPDATE_PUBLIC_POST_STATUS_R = re_compile(fr'^{UPDATE_PUBLIC_POST_STATUS}', )


class Cmds(str, Enum):
    POST = f'/{POST_S}'
    GET_PUBLIC_POST = f'/{GET_PUBLIC_POST_S}'
    GET_MY_PERSONAL_POSTS = f'/{GET_MY_PERSONAL_POSTS_S}'
    CREATE_PUBLIC_POST = f'/{CREATE_PUBLIC_POST_S}'
    CREATE_PERSONAL_POST = f'/{CREATE_PERSONAL_POST_S}'
    SHARE_PERSONAL_POSTS = f'/{SHARE_PERSONAL_POSTS_S}'
    REQUEST_PERSONAL_POSTS = f'/{REQUEST_PERSONAL_POSTS_S}'


class Regex:
    # ^ - exactly starts with
    # $ - exactly ends with
    # \d+ - Any count of digits. just \d is only single digit
    EMPTY = EMPTY_CBK_R
    # create_public_post cmd available in inline mode, TG automatically adds "/start" cmd as prefix in this mode
    CREATE_PUBLIC_POST = re_compile(fr'^/({CREATE_PUBLIC_POST_S}|{START_S} {CREATE_PUBLIC_POST_S})$', IGNORECASE)
    CREATE_PERSONAL_POST = re_compile(CREATE_PERSONAL_POST_S, IGNORECASE)
    SHARE_PERSONAL_POSTS = re_compile(SHARE_PERSONAL_POSTS_S, IGNORECASE)
    REQUEST_PERSONAL_POSTS = re_compile(REQUEST_PERSONAL_POSTS_S, IGNORECASE)
    READY_R = READY_R
