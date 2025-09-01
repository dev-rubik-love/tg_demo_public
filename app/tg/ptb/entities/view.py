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

from .shared.view import Shared as SharedView
from .post.view import Posts
from .collection.view import Collections
from .match.view import Match
from .user.view import Reg
from .mix.view import Mix
from .cjm.view import Cjm


if TYPE_CHECKING:
    from app.tg.ptb.entities.user.model import IUser


class View(SharedView, ):  # Need to the easiest access to a common views
    Reg: Type[Reg] = Reg
    Match: Type[Match] = Match
    Collections: Type[Collections] = Collections
    Posts: Type[Posts] = Posts
    Mix: Type[Mix] = Mix
    CJM: Type[CJM] = Cjm

    def __init__(self, user: IUser, ):
        super().__init__(user=user, )
        self.reg: Reg = self.Reg(user=user, )
        self.match: Match = self.Match(user=user, )
        self.posts: Posts = self.Posts(user=user, shared_view=self, )
        self.collections: Collections = self.Collections(
            user=user,
            posts_view=self.posts,
            shared_view=self,
        )
        self.mix: Mix = self.Mix(user=user, )
        self.cjm: Cjm = Cjm(user=user, collections_view=self.collections, shared_view=self, )
