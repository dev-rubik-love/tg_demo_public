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
from typing import TYPE_CHECKING, Type
from dataclasses import dataclass

from app.entities.post.form import PostFormDC as AppPostFormDC

from .model import PublicPost as PublicPostModel, PersonalPost as PersonalPostModel
from ..collection.model import Collection as CollectionModel
from app.tg.entities.post import form as tg_form

if TYPE_CHECKING:
    from telegram import Message
    from ..user.model import IUser
    from .model import IPublicPost as IPublicPostModel, IPersonalPost as IPersonalPostModel


@dataclass
class PostFormDC(AppPostFormDC, ):
    message: Message | None = None


class IPublic(tg_form.IPublicPost, ABC, ):
    collection_names: set
    author: IUser
    message: Message
    channel_id: int

    class Mapper:
        Post: Type[IPublicPostModel]

    @abstractmethod
    def create(self, ) -> IPublicPostModel:
        ...


class Public(tg_form.PublicPost, PostFormDC, IPublic, ):  # PostFormDC overrides and should be after TgPublicPost

    class Mapper:
        Post = PublicPostModel

    def create(self, ) -> IPublicPostModel:
        post = super().create()
        post.message = self.message  # Base form doesn't know about message (only message_id)
        return post


class IPersonal(tg_form.IPersonalPost, ABC, ):
    collection_names: set
    author: IUser

    class Mapper:
        Post: Type[IPersonalPostModel]
        Collection: Type[CollectionModel]


class Personal(tg_form.PersonalPost, IPersonal, ):
    author: IUser  # Just type hint

    class Mapper:
        Post = PersonalPostModel
        Collection = CollectionModel

    def __init__(self, collection_names: set | None = None, *args, **kwargs, ):
        super().__init__(
            collection_names=collection_names or set(),
            *args,
            **kwargs,
        )
