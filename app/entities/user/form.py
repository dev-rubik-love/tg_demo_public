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
from typing import TYPE_CHECKING, Protocol
from abc import ABC, abstractmethod

# To inherit restrict properties
from rubik_core.entities.user.base import UserBaseProperties as CoreUserBaseProperties

from rubik_core.shared.structures import Goal as SharedGoal, Gender as SharedGender
from rubik_core.entities.user.exceptions import IncorrectProfileValue
from rubik_core.entities.user.model import User
from .texts import Reg

from ..shared.constants import BACK_R, SKIP_R

if TYPE_CHECKING:
    from rubik_core.entities.user.model import IUser


class NewUserProtocol(Protocol, ):
    user: IUser
    fullname: str
    goal: SharedGoal
    gender: SharedGender
    age: int | None
    country: str | None
    city: str | None
    comment: str | None
    photos: list[str]


class INewUser(NewUserProtocol, ABC, ):

    Goal: User.Goal
    Gender: IUser.Gender

    back_btn_disabled: bool

    @abstractmethod
    def _repr(self, ) -> dict:
        ...

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def handle_name(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_goal(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_gender(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_age(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_location_text(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_comment(self, text: str, ) -> None:
        ...

    @abstractmethod
    def add_photo(self, photo: str, ) -> bool:  # Photo is really str?
        ...

    @abstractmethod
    def remove_photos(self, ) -> bool:
        ...

    @abstractmethod
    def create(self, ) -> None:
        ...


class NewUser(CoreUserBaseProperties, INewUser, ):
    """Base NewUser Logic across whole app. Should be inherited `for frameworks"""

    Goal = SharedGoal
    Gender = SharedGender

    back_btn_disabled: bool = True

    def __init__(
            self,
            user: IUser,
            fullname: str | None = None,
            goal: Goal | None = None,
            gender: SharedGender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
    ):
        super().__init__(
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos or [],
        )
        self.user: IUser = user

    def _repr(self, ) -> dict:
        return CoreUserBaseProperties._repr(self=self, ) | {'id': self.user.id, }

    def __repr__(self, ) -> str:
        return repr(self._repr())

    def handle_name(self, text: str, ) -> None:
        if not BACK_R.match(text) or self.back_btn_disabled:
            self.fullname = text

    def handle_goal(self, text: str, ) -> None:
        """The same behavior as app.forms.user.Target.handle_goal. Dirty a bit"""
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if text == Reg.Buttons.I_WANNA_CHAT.lower():
                self.goal = self.Goal.CHAT
            elif text == Reg.Buttons.I_WANNA_DATE.lower():
                self.goal = self.Goal.DATE
            elif text == Reg.Buttons.I_WANNA_CHAT_AND_DATE.lower():
                self.goal = self.Goal.BOTH
            else:
                raise IncorrectProfileValue

    def handle_gender(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if text == Reg.Buttons.I_MALE.lower():
                self.gender = self.Gender.MALE
            elif text == Reg.Buttons.I_FEMALE.lower():
                self.gender = self.Gender.FEMALE
            else:
                raise IncorrectProfileValue

    def handle_age(self, text: str, ) -> None:
        text = text.lower().strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if SKIP_R.match(text):
                self.age = None  # Update if user set some value before
            elif age := ''.join([letter for letter in text if letter.isdigit()]):
                self.age = int(age)
            else:
                raise IncorrectProfileValue

    def handle_location_text(self, text: str, ) -> None:
        text = text.strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if SKIP_R.match(text):
                self.country = None
                self.city = None
            else:
                location = text.split(sep=',', maxsplit=1)
                self.country = location[0].strip()
                if len(location) > 1:  # If user specified a city too
                    self.city = location[1].strip()

    def handle_comment(self, text: str, ) -> None:
        text = text.strip()
        if not BACK_R.match(text) or self.back_btn_disabled:
            if SKIP_R.match(text):
                self.comment = None
            else:
                self.comment = text

    def add_photo(self, photo: str, ) -> bool:  # Photo is really str?
        if len(self.photos) < self.MAX_PHOTOS_COUNT:  # Don't use <= because post here post append
            self.photos.append(photo)
            return True
        return False

    def remove_photos(self, ) -> bool:
        if self.photos:
            self.photos.clear()
            return True
        else:
            return False

    def create(self, ) -> None:
        """
        Save user via form fields
        P.S. User has "save" method but it's saves instance fields
        """
        self.user.CRUD.upsert(
            user_id=self.user.id,
            fullname=self.fullname,
            goal=self.goal,
            gender=self.gender,
            age=self.age,
            country=self.country,
            city=self.city,
            comment=self.comment,
            connection=self.user.connection,
        )
        self.user.delete_photos()  # Delete old user_photos
        for photo in self.photos:
            self.user.Photo.create(user=self.user, photo=photo, )
        self.user.is_registered = True
