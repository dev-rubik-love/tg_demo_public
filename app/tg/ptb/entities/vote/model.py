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
from abc import ABC
from typing import Type, TYPE_CHECKING

from app.tg.entities.vote.model import (
    PublicVote as TgPublicVote,
    IPublicVote as ITgPublicVote,
    PersonalVote as TgPersonalVote,
    IPersonalVote as ITgPersonalVote,
)

if TYPE_CHECKING:
    from telegram import CallbackQuery
    from ..user.model import IUser
    from ..post.model import IPublicPost, IPersonalPost


class VoteBase:
    @classmethod
    def from_callback(
            cls: Type[IPublicVote | IPersonalVote],
            user: IUser,
            callback: CallbackQuery,
    ) -> IPublicVote | IPersonalVote:
        """Convert str callback to vote object"""
        post_id = vote_value = int(callback.data.split()[-1])
        # from_user is None for channels and may not exist for MaybeInaccessibleMessage
        if getattr(callback.message, 'from_user', None, ):
            # noinspection PyUnresolvedReferences
            channel_id = callback.message.from_user.id
        else:
            channel_id = callback.message.chat.id
        return cls(
            user=user,
            post_id=abs(post_id),
            channel_id=channel_id,
            message_id=callback.message.message_id,
            value=cls.convert_vote_value(raw_value=vote_value),
        )


class IPublicVote(ITgPublicVote, ABC, ):
    Post: Type[IPublicPost]
    User: Type[IUser]


class PublicVote(TgPublicVote, VoteBase, IPublicVote, ):
    Post: Type[IPublicPost]
    User: Type[IUser]


class IPersonalVote(ITgPersonalVote, ABC, ):
    Post: Type[IPersonalPost]
    User: Type[User]


class PersonalVote(TgPersonalVote, VoteBase, IPersonalVote, ):
    Post: Type[IPersonalPost]
    User: Type[User]
