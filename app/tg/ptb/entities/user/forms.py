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
from typing import TYPE_CHECKING, Sequence
from abc import ABC, abstractmethod

from geopy.exc import GeocoderServiceError

from app.entities.shared.exceptions import LocationServiceError, BadLocation
from rubik_core.shared.structures import Gender as GenderStruct, Goal as GoalStruct
from app.postconfig import locator as yandex_locator
from app.tg.entities.user.form import (
    NewUser as TgNewUserForm,
    INewUser as ITgNewUserForm,  # Need to inheritance
)

from .view import Keyboards
from .texts import Reg as RegTexts

if TYPE_CHECKING:
    from geopy.geocoders.yandex import Yandex as YandexLocator
    from telegram import (
        PhotoSize,
        ReplyKeyboardMarkup as tg_RKM,
        Location as tg_Location,
    )
    from .model import IUser


class INewUser(ITgNewUserForm, ABC, ):
    original_photo_keyboard: tg_RKM
    remove_photos_keyboard: tg_RKM
    current_keyboard: tg_RKM

    @abstractmethod
    def handle_location_geo(self, location: tg_Location) -> None:
        ...

    @abstractmethod
    def handle_photo_tg_object(self, photo: Sequence[PhotoSize], media_group_id: str | None, ) -> str | None:
        ...

    @abstractmethod
    def add_account_photos(self, ) -> str:
        ...

    @abstractmethod
    def is_reply_on_photo(self, media_group_id: str | None) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def convert_tg_photo(photo: Sequence[PhotoSize], ) -> str:
        ...


class NewUser(TgNewUserForm, INewUser, ):
    """TG class to register user (keep temporary data and handle it)"""
    original_photo_keyboard: tg_RKM = Keyboards.original_photo_keyboard
    remove_photos_keyboard: tg_RKM = Keyboards.remove_photos_keyboard
    locator: YandexLocator = yandex_locator
    user: IUser  # Just typehint for pycharm

    def __init__(
            self,
            user: IUser,
            fullname: str | None = None,
            goal: GoalStruct | None = None,
            gender: GenderStruct | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
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
        self.current_keyboard: tg_RKM = self.original_photo_keyboard
        # For internal usage as condition
        self._old_media_group_id: str | None = None  # String because in TG API it has str type

    def __repr__(self, ) -> str:
        # noinspection PyProtectedMember
        d = super()._repr() | {
            '_old_media_group_id': self._old_media_group_id,
            'current_keyboard': self.current_keyboard,
        }
        return repr({k: v for k, v in d.items() if v is not None})

    async def handle_name(self, text: str) -> None:
        """Override base method because here exists account name"""
        text = text.lower()
        if text.startswith(RegTexts.Buttons.USE_ACCOUNT_NAME.lower()):
            self.fullname = self.user.ptb.name
        else:
            super().handle_name(text=text, )

    def handle_location_geo(self, location: tg_Location) -> None:
        # TODO make app location object
        try:
            resolved_location = self.locator.reverse(
                query=f'{location.latitude}, {location.longitude}',
                exactly_one=True,
            )
        except GeocoderServiceError:
            raise LocationServiceError(location)
        try:  # TODO error prone geo
            str_location = resolved_location.address.split(',')
            self.city = str_location[-2].strip()
            self.country = str_location[-1].strip()
        except IndexError:
            raise BadLocation(location)

    def handle_photo_tg_object(self, photo: Sequence[PhotoSize], media_group_id: str | None, ) -> str | None:
        """
        Handle ptb photo indeed
        Тут мини баг. Если отправить 2 группы подряд - будет 2 сообщения о превышении,
        потому что после 10 фото альбому назначается новый айди
        """
        converted_photo = self.convert_tg_photo(photo=photo, )
        if self.add_photo(photo=converted_photo, ) is True:
            if self.is_reply_on_photo(media_group_id=media_group_id, ) is True:
                # Change keyboard here?
                return RegTexts.PHOTO_ADDED_SUCCESS
        else:
            self.current_keyboard = self.remove_photos_keyboard
            return RegTexts.TOO_MANY_PHOTOS
        return None

    async def add_account_photos(self, ) -> str:
        user_profile_photos = []
        user_profile_photos_obj = await self.user.ptb.get_profile_photos(
            limit=self.user.MAX_PHOTOS_COUNT - len(self.photos),  # TODO warn beforehand
        )
        # Probably wrong type hint that claims that user_profile_photos_obj may be None
        if user_profile_photos_obj:  # Don't use "or" cuz final list should be unpacked anyway (.photos)
            user_profile_photos = user_profile_photos_obj.photos
        if user_profile_photos:  # : list[list[PhotoSize]]
            self.current_keyboard = self.remove_photos_keyboard
            for ptb_photosize_obj in user_profile_photos:
                photo = self.convert_tg_photo(photo=ptb_photosize_obj, )
                if self.add_photo(photo=photo, ) is False:  # is photo added success
                    return RegTexts.TOO_MANY_PHOTOS
            return RegTexts.PHOTOS_ADDED_SUCCESS
        else:
            return RegTexts.NO_PROFILE_PHOTOS

    def is_reply_on_photo(self, media_group_id: str | None) -> bool:
        """media_group_id need to find out is bot should react with message on the send group of photos"""
        result = media_group_id is None or media_group_id != self._old_media_group_id  # None need
        self._old_media_group_id = media_group_id
        return result  # Check should be before assignment

    def remove_uploaded_photos(self, ) -> str:
        """Layer of PTB exactly"""
        if result := super().remove_uploaded_photos():
            self._old_media_group_id = None
            self.current_keyboard = self.original_photo_keyboard
        return result

    @staticmethod
    def convert_tg_photo(photo: Sequence[PhotoSize], ) -> str:
        """TG photo object is list of 4 photos with a different quality, last item is the best quality"""
        return photo[-1].file_id
