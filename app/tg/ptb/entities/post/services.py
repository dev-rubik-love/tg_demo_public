from __future__ import annotations
from typing import TYPE_CHECKING, Type
from abc import ABC, abstractmethod
from time import sleep as time_sleep

from telegram.error import TelegramError

from rubik_core.entities.post.service import PublicPost as PublicPostService

from . import model
from ..mix.services import System

if TYPE_CHECKING:
    from telegram import Message
    from ..user.model import IUser
    from ..mix.services import ISystem


class IBotPublicPost(ABC, ):
    System: Type[ISystem]

    @classmethod
    @abstractmethod
    def mass_update_keyboard_job(cls, bot_post: model.IBotPublicPost, ) -> list[Message]:
        ...

    @classmethod
    @abstractmethod
    def get_voted_users(
            cls,
            post: model.IBotPublicPost,
    ) -> list[IUser]:
        ...


class BotPublicPost(IBotPublicPost, ):
    System: Type[ISystem] = System

    @classmethod
    async def mass_update_keyboard_job(cls, bot_post: model.IBotPublicPost, ) -> list[Message]:
        """Mass update keyboard for users if some vote was set/changed"""
        result = []
        for user in cls.get_voted_users(post=bot_post, ):  # Only voted users have a message to update
            vote = cls.System.Mapper.PublicVote.read(post_id=bot_post.id, user=user, )
            try:
                sent_message = await bot_post.update_poll_keyboard(clicker_vote=vote, )
            except TelegramError:
                continue  # Do nothing if user not exists (no need to delete, he may come back)
            result.append(sent_message)
            time_sleep(1)
        return result

    @classmethod
    def get_voted_users(
            cls,
            post: model.IBotPublicPost,
    ) -> list[IUser]:
        return post.get_voted_users(connection=cls.System.user.connection, )


class PublicPost(PublicPostService, ):
    class Mapper:
        PublicPost = model.PublicPost
