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
from typing import TYPE_CHECKING, Type
from abc import ABC

from app.tg.entities.collection.model import (
    Collection as TGCollection,
    ICollection as ITgCollection,
)
if TYPE_CHECKING:
    from ..user.model import IUser
    from ..post.model import IPublicPost, IPersonalPost


class ICollection(ITgCollection, ABC, ):
    PublicPost: Type[IPublicPost]
    PersonalPost: Type[IPersonalPost]
    User: Type[IUser]


class Collection(TGCollection, ICollection, ):
    """Collection may content either public or personal posts"""
