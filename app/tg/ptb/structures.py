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
from typing import TYPE_CHECKING, Any, Iterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from telegram import InlineKeyboardButton as tg_IKB
    from rubik_core.db.manager import connection_type
    from app.tg.ptb.entities.view import View
    from app.tg.ptb.entities.user.model import IUser
    from app.tg.ptb.entities.collection.model import ICollection
    from app.tg.ptb.entities.post.model import IPublicPost
    from app.tg.ptb.entities.user.forms import INewUser as INewUserForm
    from app.tg.ptb.entities.match.forms import ITarget as ITargetForm
    from app.tg.ptb.entities.post.forms import IPublic as IPublicPostForm, IPersonal as IPersonalPostForm


class IKeyboard(ABC, ):

    @abstractmethod
    def build_callback(self, *args: Any, **kwargs: Any, ) -> str:
        ...

    @abstractmethod
    def build_inline_button(self, *args: Any, **kwargs: Any, ) -> tg_IKB:
        ...

    @classmethod
    @abstractmethod
    def extract_cbk_data(cls, cbk_data: str, ) -> Any:
        ...


@dataclass(slots=True)
class CustomUserData:

    @dataclass(slots=True)
    class Forms:
        new_user: INewUserForm | None = None
        target: ITargetForm | None = None
        public_post: IPublicPostForm | None = None
        personal_post: IPersonalPostForm | None = None

    @dataclass
    class TmpData:
        """ Temporary data, don't apply slots here, any data may be here"""

        @dataclass(slots=True)
        class CollectionsToShare:  # Move to forms?
            message_id_with_collections: int
            ids: set[int] = field(default_factory=set, )

        collections_to_share: CollectionsToShare | None = None

    connection: connection_type | None = None
    view: View | None = None
    model: IUser | None = None
    tmp_data: TmpData = field(default_factory=TmpData, )
    forms: Forms = field(default_factory=Forms, )


@dataclass(order=True, )
class InlinePost:
    post: IPublicPost = field(compare=False, )
    # type: str = field(compare=False, )  # str type of the message got by telegram.helpers.effective_message_type
    priority: int = field(compare=True, default=0, )  # Compare (<==>) only by this field


@dataclass(slots=True, )
class PostsCategories:
    photos: list[InlinePost] = field(default_factory=list, )
    videos: list[InlinePost] = field(default_factory=list, )
    texts: list[InlinePost] = field(default_factory=list, )
    documents: list[InlinePost] = field(default_factory=list, )

    @property
    def all(self) -> list[InlinePost]:
        return self.photos + self.videos + self.texts + self.documents

    def __iter__(self) -> Iterator[list[InlinePost]]:
        """Итерация по всем сообщениям."""
        yield from (self.photos, self.videos, self.texts, self.documents, )


@dataclass
class InlineData:
    collections: list[ICollection] = field(default_factory=list, )  # No need "priority" field and can be used directly
    posts: PostsCategories = field(default_factory=PostsCategories, )


@dataclass(slots=True, )
class CustomBotData:
    inline_data = InlineData()
