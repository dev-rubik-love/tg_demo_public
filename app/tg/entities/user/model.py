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
from abc import ABC, abstractmethod

from rubik_core.entities.user.model import User as AppUser, IUser as IAppUser

if TYPE_CHECKING:
    from rubik_core.shared.structures import Goal
    from psycopg2.extensions import connection as pg_ext_connection


class IUser(IAppUser, ABC, ):
    @abstractmethod
    def is_tg_active(self) -> bool:  # Not in use mainly
        ...


class User(AppUser, IUser, ):
    """User with methods of telegram"""

    def __init__(
            self,
            id: int,
            connection: pg_ext_connection | None = None,
            tg_name: str | None = None,
            fullname: str | None = None,
            goal: Goal | None = None,
            gender: IAppUser.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
            is_registered: bool = False,
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
        self._tg_name = tg_name
        self._is_tg_active = is_tg_active

    def is_tg_active(self) -> bool:  # Not in use mainly
        raise NotImplementedError
