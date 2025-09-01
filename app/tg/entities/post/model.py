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
from typing import TYPE_CHECKING
from abc import ABC

from rubik_core.entities.post.model import (
    Public as AppPublicPost,
    IPublic as IAppPublicPost,
    Personal as AppPersonalPost,
    IPersonal as IAppPersonalPost,
    VotedPublicPost as AppVotedPublicPost,
    IVotedPublicPost as IAppVotedPublicPost,
    VotedPersonalPost as AppVotedPersonalPost,
    IVotedPersonalPost as IAppVotedPersonalPost,
)

if TYPE_CHECKING:
    from rubik_core.entities.user.model import IUser as ICoreUser


class IBotPublicPost(IAppPublicPost, ABC, ):
    ...


class BotPublicPost(AppPublicPost, IBotPublicPost, ):
    ...


class IPublicPost(IAppPublicPost, ABC, ):
    posts_channel_message_id: int


class PublicPost(AppPublicPost, IPublicPost, ):
    def __init__(
            self,
            id: int,
            author: ICoreUser,
            channel_id: int,
            message_id: int,
            posts_channel_message_id: int = None,
            likes_count: int = 0,
            dislikes_count: int = 0,
            status: AppPublicPost.Status = AppPublicPost.Status.PENDING,
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
        self.posts_channel_message_id = posts_channel_message_id


class IBotPersonalPost(IAppPersonalPost, ABC):
    pass


class BotPersonalPost(AppPersonalPost, IBotPersonalPost, ):
    pass


class IPersonalPost(IAppPersonalPost, ABC):
    pass


class PersonalPost(AppPersonalPost, IPersonalPost, ):
    pass


class IVotedPublicPost(IAppVotedPublicPost, ABC, ):
    pass


class VotedPublicPost(AppVotedPublicPost, IVotedPublicPost, ):
    pass


class IVotedPersonalPost(IAppVotedPersonalPost, ABC, ):
    pass


class VotedPersonalPost(AppVotedPersonalPost, IVotedPersonalPost, ):
    pass
