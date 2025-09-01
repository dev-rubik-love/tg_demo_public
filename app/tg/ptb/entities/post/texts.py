from __future__ import annotations
from types import SimpleNamespace
from typing import TYPE_CHECKING

from app.entities.post.texts import Post
from app.entities.shared.texts import CmdDescriptions, INTERNAL_ERROR

from .constants import Cmds

if TYPE_CHECKING:
    pass


class Posts(Post, ):
    class Public(Post.Public):
        CMD_DESCRIPTIONS = SimpleNamespace(
            CREATE_PUBLIC_POST=f'{Cmds.CREATE_PUBLIC_POST} - {CmdDescriptions.PUBLIC_POST}\n',
            GET_PUBLIC_POST=f'{Cmds.GET_PUBLIC_POST} - {CmdDescriptions.GET_NEW_PUBLIC_POST}\n',
        )

    class Personal(Post.Personal, ):
        CMD_DESCRIPTIONS = SimpleNamespace(
            GET_MY_PERSONAL_POSTS=f'{Cmds.GET_MY_PERSONAL_POSTS} - {CmdDescriptions.GET_PERSONAL_POSTS}\n',
            REQUEST_PERSONAL_POSTS=f'{Cmds.REQUEST_PERSONAL_POSTS} - {CmdDescriptions.REQUEST_PERSONAL_POSTS}\n',
            SHARE_PERSONAL_POSTS=f'{Cmds.SHARE_PERSONAL_POSTS} - {CmdDescriptions.SHARE_PERSONAL_POSTS}\n',
            CREATE_PERSONAL_POST=f'{Cmds.CREATE_PERSONAL_POST} - {CmdDescriptions.PERSONAL_POST}\n',
        )
        USER_ACCEPTED_SHARE_PROPOSAL = Post.Personal.USER_ACCEPTED_SHARE_PROPOSAL
        NO_POSTS = Post.Personal.NO_POSTS.format(
            CREATE_PERSONAL_POST_CMD=Cmds.CREATE_PERSONAL_POST,
        )

    INTERNAL_ERROR = INTERNAL_ERROR
