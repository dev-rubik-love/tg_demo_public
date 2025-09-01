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
from typing import TYPE_CHECKING, TypeAlias
from abc import ABC, abstractmethod

from app.entities.user.texts import Reg as AppRegTexts
from app.entities.user.form import NewUser as AppNewUser, INewUser as IAppNewUser

from app.entities.shared.constants import BACK_R, SKIP_R

if TYPE_CHECKING:
    from .model import IUser

Goal: TypeAlias = AppNewUser.Goal
Gender: TypeAlias = AppNewUser.Gender


class INewUser(IAppNewUser, ABC, ):
    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    async def add_account_photos(self, ) -> str | None:
        ...

    @abstractmethod
    async def handle_photo_text(self, text: str, ) -> str | None:
        ...

    @abstractmethod
    def remove_uploaded_photos(self, ) -> str:
        ...


class NewUser(AppNewUser, IAppNewUser, ):
    """TG class to register user (keep temporary data and handle it)"""

    def __init__(
            self,
            user: IUser,
            fullname: str | None,
            goal: Goal | None,
            gender: Gender | None,
            age: int | None,
            country: str | None,
            city: str | None,
            comment: str | None,
            photos: list[str] | None = None
    ):  # Load previous reg values?
        super().__init__(
            user=user,
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos
        )

    def __repr__(self) -> str:  # pragma: no cover
        return super().__repr__()  # type: ignore[safe-super]

    async def add_account_photos(self, ) -> str | None:
        """handle_photo_text has this option"""
        raise NotImplementedError()

    async def handle_photo_text(self, text: str, ) -> str | None:
        text = text.lower().strip()
        if BACK_R.match(text) and not self.back_btn_disabled:  # Currently always False
            return None
        elif text == AppRegTexts.Buttons.REMOVE_PHOTOS.lower():
            return self.remove_uploaded_photos()
        elif text == AppRegTexts.Buttons.USE_ACCOUNT_PHOTOS.lower():
            return await self.add_account_photos()
        elif text == AppRegTexts.Buttons.FINISH.lower() or SKIP_R.match(text.lower()):
            return AppRegTexts.Buttons.FINISH  # No del on skip
        else:
            return AppRegTexts.INCORRECT_FINISH  # raise?

    def remove_uploaded_photos(self, ) -> str:
        """Layer of behavior"""
        result = self.remove_photos()
        if result is True:
            return AppRegTexts.PHOTOS_REMOVED_SUCCESS
        else:
            return AppRegTexts.NO_PHOTOS_TO_REMOVE
