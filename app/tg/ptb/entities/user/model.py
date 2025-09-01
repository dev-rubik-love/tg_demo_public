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
from abc import ABC, abstractmethod

from telegram.error import TelegramError
from telegram import User as PtbUser

from app.tg.entities.user.model import (
    User as TgUser,
    IUser as ITgUser,
)

from app.tg.ptb import bot

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    from telegram.ext import ExtBot
    from ..match.model import IMatcher
    from ..collection.model import ICollection
    from ..post.model import IPublicPost, IPersonalPost
    from ..vote.model import IPublicVote, IPersonalVote


class IUser(ITgUser, ABC, ):
    bot: ExtBot = bot
    PublicVote: Type[IPublicVote]
    PersonalVote: Type[IPersonalVote]
    PublicPost: Type[IPublicPost]
    PersonalPost: Type[IPersonalPost]
    Collection: Type[ICollection]
    Matcher: Type[IMatcher]

    _is_tg_active: bool
    ptb: PtbUser

    @abstractmethod
    async def check_is_tg_active(self, ) -> bool:
        """Not in use mainly"""

    @abstractmethod
    def get_vote(self, post: IPublicPost | IPersonalPost, ) -> IPublicVote | IPersonalVote:
        ...


class User(TgUser, IUser, ):
    """User with methods of telegram"""
    bot: ExtBot = bot
    PublicVote: Type[IPublicVote]
    PersonalVote: Type[IPersonalVote]
    PublicPost: Type[IPublicPost]
    PersonalPost: Type[IPersonalPost]
    Collection: Type[ICollection]
    Matcher: Type[IMatcher]

    def __init__(
            self,
            id: int,
            ptb: PtbUser | None = None,
            connection: pg_ext_connection | None = None,
            fullname: str | None = None,
            goal: IUser.Goal | None = None,
            gender: IUser.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
            is_registered: bool | None = None,
            is_tg_active: bool = True,
    ):
        super().__init__(
            id=id,
            connection=connection,
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos,
            is_registered=is_registered,
        )
        self.ptb = ptb or PtbUser(id=id, first_name='', is_bot=False, )
        self.is_tg_active = is_tg_active

    async def check_is_tg_active(self, ) -> bool:  # Not in use mainly
        """86400 - 24 hours"""
        try:
            self.is_tg_active = bool(await self.bot.get_chat(self.id, read_timeout=2, ))
        except TelegramError:
            self.is_tg_active = False
        return self.is_tg_active
