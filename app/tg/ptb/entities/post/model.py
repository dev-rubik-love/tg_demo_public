# Copyright (C) 2023 David Shiko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Type
from dataclasses import dataclass

from rubik_core.entities.post.model import VotedPost, IVotedPost

from app.tg.entities.post import model as tg_post

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    from telegram import CallbackQuery, Message
    from rubik_core.db.manager import Params as DbParams
    from ..vote.model import IPublicVote, IPersonalVote
    from ..user.model import IUser

PostBaseType = TypeVar('PostBaseType', bound='PostBase')


class Shared:
    """Shared methods"""

    @classmethod
    def from_callback(
            cls: Type[PostBaseType],
            callback: CallbackQuery,
            connection: pg_ext_connection,
    ) -> PostBaseType | None:
        """Interface to read a full post by incoming id"""
        post_id = abs(int(callback.data.split()[-1]))
        return cls.read(post_id=post_id, connection=connection, )


class IBotPublicPost(tg_post.IBotPublicPost, ABC, ):
    """Bot Post is post intended to be used inside bot (not a post channel)."""

    message: Message

    @classmethod
    @abstractmethod
    def from_callback(cls, callback: CallbackQuery, connection: pg_ext_connection) -> IPublicPost:
        ...


class BotPublicPost(Shared, tg_post.BotPublicPost, IBotPublicPost, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""

    def __init__(
            self,
            id: int,
            author: IUser,
            channel_id: int,
            message_id: int,
            message: Message | None = None,
            likes_count: int = 0,
            dislikes_count: int = 0,
            status: tg_post.BotPublicPost.Status = tg_post.BotPublicPost.Status.PENDING,
    ):
        super().__init__(
            id=id,
            author=author,
            channel_id=channel_id,
            message_id=message_id,
            likes_count=likes_count,
            dislikes_count=dislikes_count,
            status=status,
        )
        self.message = message


class IPublicPost(tg_post.IPublicPost, ABC, ):
    Vote: Type[IPublicVote]
    User: Type[IUser]

    message: Message

    @classmethod
    @abstractmethod
    def from_callback(cls, callback: CallbackQuery, connection: pg_ext_connection) -> IPublicPost:
        ...


class PublicPost(Shared, tg_post.PublicPost, IPublicPost, ):

    Vote: Type[IPublicVote]
    User: Type[IUser]

    def __init__(
            self,
            id: int,
            author: IUser,
            channel_id: int,
            message_id: int,
            likes_count: int = 0,
            dislikes_count: int = 0,
            status: IPublicPost.Status = tg_post.PublicPost.Status.PENDING,
            message: Message | None = None,
    ):
        super().__init__(
            id=id,
            author=author,
            channel_id=channel_id,
            message_id=message_id,
            likes_count=likes_count,
            dislikes_count=dislikes_count,
            status=status,
        )
        self.message = message

    @classmethod
    def read_mass(cls, status: tg_post.PublicPost.Status | None = None, ) -> tg_post.PublicPost | None:
        if post := super().read_mass(status=status, ):
            return cls(**post)  # TODO unpack the post


class IChannelPublicPost(tg_post.IPublicPost, ABC, ):

    @classmethod
    @abstractmethod
    def read(cls, post_id: int, connection: pg_ext_connection) -> IChannelPublicPost | None:
        ...

    @abstractmethod
    def unpublish(self, ) -> None:
        pass


class ChannelPublicPost(Shared, tg_post.PublicPost, IChannelPublicPost, ):

    @classmethod
    def read(cls, post_id: int, connection: pg_ext_connection) -> IChannelPublicPost | None:
        post = super().read(post_id=post_id, connection=connection, )
        if post:
            post.posts_channel_message_id = post.CRUD.read_public_post_channel_message_id(
                post_id=post_id,
                connection=connection,
            )
        return post

    def publish(self, ) -> None:
        """update_status and message_id"""
        self.update_status(status=self.Status.RELEASED, )
        self.CRUD.update_posts_channel_message_id(
            post_id=self.id,
            message_id=self.posts_channel_message_id,
            connection=self.author.connection,
        )

    def unpublish(self, db_params: DbParams | None = None, ) -> None:
        """update_status and message_id"""
        if self.status == self.Status.RELEASED:
            self.CRUD.update_posts_channel_message_id(
                post_id=self.id,
                message_id=None,
                connection=getattr(db_params, 'connection,', self.author.connection, )
            )
            self.update_status(status=self.Status.READY_TO_RELEASE, )

    @classmethod
    def read_mass(cls, status: tg_post.PublicPost.Status | None = None, ) -> tg_post.PublicPost | None:
        if post := super().read_mass(status=status, ):
            return cls(**post)  # TODO unpack the post


class IBotPersonalPost(tg_post.IBotPersonalPost, ABC):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""


class BotPersonalPost(tg_post.BotPersonalPost, IBotPersonalPost, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""


class IPersonalPost(tg_post.IPersonalPost, ABC, ):
    Vote: Type[IPersonalVote]
    User: Type[IUser]

    @classmethod
    @abstractmethod
    def extract_cbk_data(cls, callback_data: str) -> tuple[IUser, bool]:
        ...

    @classmethod
    @abstractmethod
    def from_callback(cls, callback: CallbackQuery, connection: pg_ext_connection) -> IPersonalPost:
        ...


class PersonalPost(Shared, tg_post.PersonalPost, IPersonalPost, ):
    Vote: Type[IPersonalVote]
    User: Type[IUser]

    @classmethod
    def extract_cbk_data(cls, callback_data: str, ) -> tuple[IUser, bool]:
        """
        Get payload of callback
        Not a part of logic (domain) object
        """
        _, str_recipient_id, flag = callback_data.split()
        return cls.User(id=int(str_recipient_id), ), bool(int(flag))


class IVotedPublicPost(tg_post.IVotedPublicPost, ABC, ):
    post: IPublicPost
    clicker_vote: PublicPost.Vote


@dataclass
class VotedPublicPost(tg_post.VotedPublicPost, IVotedPublicPost, ):
    post: IPublicPost
    clicker_vote: PublicPost.Vote


class IVotedPersonalPost(tg_post.IVotedPersonalPost, ABC, ):
    post: IPersonalPost
    clicker_vote: IPersonalVote
    opposite_vote: IPersonalVote | None  # If showing to myself  (make another class ?)


@dataclass
class VotedPersonalPost(tg_post.VotedPersonalPost, IVotedPersonalPost, ):
    post: PersonalPost
    clicker_vote: PersonalPost.Vote
    opposite_vote: PersonalPost.Vote | None  # If showing to myself  (make another class ?)


class IVotedPost(IVotedPost, ABC, ):
    Public: IPublicPost
    Personal: IPersonalPost


class VotedPost(VotedPost, ):
    Public = VotedPublicPost
    Personal = VotedPersonalPost
