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
from typing import TYPE_CHECKING, Type, Protocol, ClassVar
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from rubik_core.entities.collection.model import Collection as AppCollection
from rubik_core.entities.post.model import (
    Public as AppPublicPost,
    Personal as AppPersonalPost,
)

if TYPE_CHECKING:
    from rubik_core.entities.user.model import IUser as ICoreUser
    from rubik_core.entities.post.model import (
        IPublic as IAppPublicPostModel,
        IPersonal as IAppPersonalPostModel,
    )
    from rubik_core.entities.collection.model import ICollection as IAppCollection


@dataclass
class PostFormProtocol(Protocol, ):
    author: ICoreUser
    message_id: int
    collection_names: set[str]
    user_collections_count: int  # Perhaps should be moved to user space
    MAX_COLLECTIONS_COUNT: ClassVar[int]  # See https://stackoverflow.com/a/59904697


@dataclass
class PostFormDC:
    author: ICoreUser
    channel_id: int
    message_id: int
    collection_names: set[str] = field(default_factory=set, )
    user_collections_count: int = 0  # Perhaps should be moved to user space

    # ClassVar - Set as cls attr rather than instance (unannotated or special annotated fields) remain cls attrs
    MAX_COLLECTIONS_COUNT: ClassVar[int] = 10  # See https://stackoverflow.com/a/59904697


class IPublicPost(PostFormProtocol, ABC, ):

    class Mapper:
        Post: Type[IAppPublicPostModel]

    @abstractmethod
    def create(self, ) -> IAppPublicPostModel:
        ...


class PublicPost(PostFormDC, IPublicPost, ):
    class Mapper:
        Post: Type[IAppPublicPostModel] = AppPublicPost

    def create(self, ) -> IAppPublicPostModel:
        post = self.Mapper.Post.create(
            author=self.author,
            channel_id=self.channel_id,
            message_id=self.message_id,
        )
        return post


class IPersonalPost(PostFormProtocol, ABC, ):

    class Mapper:
        Post: Type[IAppPersonalPostModel]
        Collection: Type[IAppCollection]

    MAX_COLLECTION_NAME_LEN: int

    @abstractmethod
    def create(self, *args, **kwargs, ) -> IPersonalPost:
        ...

    def handle_collection_names(self, text: str, ) -> None:
        """Handle collection names got from user input"""

    def handle_collection_name_btn(self, collection_name: str, is_chosen: bool, ) -> None:
        """Handle collection names got by the keyboard"""


class PersonalPost(PostFormDC, IPersonalPost, ):
    class Mapper:
        Post: Type[IAppPersonalPostModel] = AppPersonalPost
        Collection: Type[IAppCollection] = AppCollection

    MAX_COLLECTION_NAME_LEN = Mapper.Collection.MAX_NAME_LEN

    def create(self, ) -> IAppPersonalPostModel:
        post = self.Mapper.Post.create(
            author=self.author,
            channel_id=self.channel_id,
            message_id=self.message_id,
        )
        for name in self.collection_names:
            # Collection creates only association with post but not post itself
            self.Mapper.Collection.create(name=name, posts=[post], author=self.author, )
        return post

    def handle_collection_names(self, text: str, ) -> None:
        """Handle collection names got from user input"""
        # validate collections limit here cuz we just read the collections
        collections_limit = max(self.MAX_COLLECTIONS_COUNT - self.user_collections_count, 0)
        for name in text.strip().split(',')[:collections_limit]:
            name = name.strip()[:self.Mapper.Collection.MAX_NAME_LEN]
            # No need to warn about too short name cuz most likely it's user misunderstand of comma usage
            if len(name) > 0:
                self.collection_names.add(name, )
                self.user_collections_count += 1  # Inaccurate but ok

    def handle_collection_name_btn(self, collection_name: str, is_chosen: bool, ) -> None:
        """Handle collection names got by the keyboard"""
        if is_chosen and (self.MAX_COLLECTIONS_COUNT - self.user_collections_count > 0):
            self.collection_names.add(collection_name, )
            self.user_collections_count += 1  # Inaccurate but ok
        else:
            self.collection_names.remove(collection_name, )
            self.user_collections_count -= 1  # Inaccurate but ok
