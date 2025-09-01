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
from typing import TYPE_CHECKING, Type

from app.tg.entities.match.model import (
    Match as TgMatch,
    IMatch as ITgMatch,
    Matcher as TgMatcher,
    IMatcher as ITgMatcher,
    MatchStats as TgMatchStats,
    IMatchStats as ITgMatchStats,
)

if TYPE_CHECKING:
    from ..user.model import IUser


class IMatch(ITgMatch, ABC, ):
    pass


class Match(TgMatch, IMatch, ):
    pass


class IMatcher(ITgMatcher, ABC, ):
    Match: Type[IMatch]
    User: Type[IUser]


class Matcher(TgMatcher, IMatcher, ):
    Match: Type[IMatch]
    User: Type[IUser]


class IMatchStats(ITgMatchStats, ABC, ):
    user: IUser


class MatchStats(TgMatchStats, IMatchStats, ):
    user: IUser
