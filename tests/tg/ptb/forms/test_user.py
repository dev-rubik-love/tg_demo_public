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

from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from geopy.exc import GeocoderServiceError
from telegram import Location

from app.entities.shared.exceptions import BadLocation, LocationServiceError

from app.tg.entities.user.form import NewUser as TGNewUser

from app.tg.ptb.entities.user.texts import Reg as RegConstants
from app.tg.ptb.entities.user.forms import NewUser

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import PhotoSize
    from app.tg.ptb.entities.user.forms import INewUser


class TestNewUser:

    @staticmethod
    def test_repr(new_user_f: INewUser, ):
        repr(new_user_f)

    @staticmethod
    async def test_handle_name_manual(mock_new_user: MagicMock, ) -> None:
        with patch_object(
                target=NewUser.mro()[1],  # Patch parent (super) class method
                attribute='handle_name',
        ) as mock_handle_name:
            await NewUser.handle_name(self=mock_new_user, text='foo', )
        mock_handle_name.acow(self=mock_new_user, text='foo', )

    @staticmethod
    async def test_handle_name_account(mock_new_user: MagicMock, ) -> None:
        assert mock_new_user.fullname != mock_new_user.user.ptb.name
        await NewUser.handle_name(self=mock_new_user, text=RegConstants.Buttons.USE_ACCOUNT_NAME, )
        assert mock_new_user.fullname == mock_new_user.user.ptb.name

    @staticmethod
    def test_handle_location_geo_bad_location(mock_new_user: MagicMock, tg_location: Location, ):
        mock_new_user.locator.reverse.return_value.address = ''
        with pytest.raises(expected_exception=BadLocation):
            NewUser.handle_location_geo(self=mock_new_user, location=tg_location, )
        mock_new_user.locator.reverse.acow(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )

    @staticmethod
    def test_handle_location_geo_service_error(mock_new_user: MagicMock, tg_location: Location, ):
        mock_new_user.locator.reverse.side_effect = GeocoderServiceError('')
        with pytest.raises(expected_exception=LocationServiceError, ):
            NewUser.handle_location_geo(self=mock_new_user, location=tg_location, )
        mock_new_user.locator.reverse.acow(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )

    @staticmethod
    def test_handle_location_geo(mock_new_user: MagicMock, tg_location: Location, ):
        mock_new_user.locator.reverse.return_value.address = 'Ставропольский край, Россия'
        NewUser.handle_location_geo(
            self=mock_new_user,
            location=Location(longitude=45, latitude=45),
        )
        mock_new_user.locator.reverse.acow(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )
        assert mock_new_user.country == 'Россия'
        assert mock_new_user.city == 'Ставропольский край'

    class TestHandlePhotoText:
        @staticmethod
        async def test_go_back(mock_new_user, ):
            """Btn is disabled currently"""
            result = await NewUser.handle_photo_text(
                self=mock_new_user,
                text=RegConstants.Buttons.BACK,
            )
            assert result == RegConstants.INCORRECT_FINISH  # GO back btn is disabled

        @staticmethod
        async def test_remove_uploaded_photos(mock_new_user, ):
            result = await NewUser.handle_photo_text(
                self=mock_new_user,
                text=RegConstants.Buttons.REMOVE_PHOTOS,
            )
            mock_new_user.remove_uploaded_photos.acow()
            assert result == mock_new_user.remove_uploaded_photos.return_value

        @staticmethod
        async def test_use_account_photos(mock_bot: MagicMock, mock_new_user, ):
            result = await NewUser.handle_photo_text(
                self=mock_new_user,
                text=RegConstants.Buttons.USE_ACCOUNT_PHOTOS,
            )
            mock_new_user.add_account_photos.acow()
            assert result == mock_new_user.add_account_photos.return_value

        @staticmethod
        async def test_finish_or_skip():
            for text in [RegConstants.FINISH_KEYWORD, RegConstants.SKIP_KEYWORD, ]:
                result = await NewUser.handle_photo_text(
                    self=typing_Any,
                    text=text,
                )
                assert result == RegConstants.FINISH_KEYWORD  # Skip or Finish should return finish

        @staticmethod
        async def test_incorrect_finish():
            result = await NewUser.handle_photo_text(self=typing_Any, text='foo', )
            assert result == RegConstants.INCORRECT_FINISH

    class TestAddAccountPhotos:

        @staticmethod
        async def body(mock_new_user: MagicMock, ):
            mock_new_user.photos = []  # Just apply take len
            result = await NewUser.add_account_photos(self=mock_new_user, )
            mock_new_user.user.ptb.get_profile_photos.acow(
                limit=mock_new_user.user.MAX_PHOTOS_COUNT - len(mock_new_user.photos),
            )
            return result

        async def test_no_photos(self, mock_new_user: MagicMock, ):
            mock_new_user.user.ptb.get_profile_photos.return_value.photos = []
            result = await self.body(mock_new_user=mock_new_user, )
            assert result == RegConstants.NO_PROFILE_PHOTOS

        async def test_too_many_photos(self, mock_new_user: MagicMock, ):
            mock_new_user.add_photo.return_value = False
            mock_new_user.user.ptb.get_profile_photos.return_value.photos = ['foo', ]
            # BEFORE
            assert mock_new_user.current_keyboard != NewUser.remove_photos_keyboard
            # EXECUTION
            result = await self.body(mock_new_user=mock_new_user, )
            # CHECKS
            mock_new_user.convert_tg_photo.acow(photo='foo', )
            mock_new_user.add_photo.acow(photo=mock_new_user.convert_tg_photo.return_value, )
            assert mock_new_user.current_keyboard == mock_new_user.remove_photos_keyboard
            assert result == RegConstants.TOO_MANY_PHOTOS

        async def test_success(self, mock_new_user: MagicMock, ):
            mock_new_user.user.ptb.get_profile_photos.return_value.photos = ['foo', ]
            # BEFORE
            assert mock_new_user.current_keyboard != NewUser.remove_photos_keyboard
            # EXECUTION
            result = await self.body(mock_new_user=mock_new_user, )
            # CHECKS
            mock_new_user.convert_tg_photo.acow(photo='foo', )
            mock_new_user.add_photo.acow(photo=mock_new_user.convert_tg_photo.return_value, )
            assert mock_new_user.current_keyboard == mock_new_user.remove_photos_keyboard
            assert result == RegConstants.PHOTOS_ADDED_SUCCESS

    class TestHandlePhotoTgObject:

        @staticmethod
        def body(photo_s: list[PhotoSize], mock_new_user: MagicMock, media_group_id: str, ):
            result = NewUser.handle_photo_tg_object(
                self=mock_new_user,
                photo=photo_s,
                media_group_id=media_group_id,
            )
            mock_new_user.convert_tg_photo.acow(photo=photo_s, )
            mock_new_user.add_photo.acow(photo=mock_new_user.convert_tg_photo.return_value, )
            return result

        def test_too_many_photos(
                self,
                mock_new_user: MagicMock,
                photo_s: list[PhotoSize],
        ):
            # BEFORE
            assert mock_new_user.current_keyboard != mock_new_user.remove_photos_keyboard
            result = self.body(
                mock_new_user=mock_new_user,
                photo_s=photo_s,
                media_group_id='1',
            )
            assert mock_new_user.current_keyboard == mock_new_user.remove_photos_keyboard
            assert result == RegConstants.TOO_MANY_PHOTOS

        def test_no_reply(
                self,
                mock_new_user: MagicMock,
                photo_s: list[PhotoSize],
        ):
            mock_new_user.add_photo.return_value = True
            result = self.body(
                mock_new_user=mock_new_user,
                photo_s=photo_s,
                media_group_id='1',
            )
            mock_new_user.is_reply_on_photo.acow(media_group_id='1', )
            assert result is None

        def test_success(
                self,
                mock_new_user: MagicMock,
                photo_s: list[PhotoSize],
        ):
            mock_new_user.add_photo.return_value = True
            mock_new_user.is_reply_on_photo.return_value = True
            # BEFORE
            assert mock_new_user.current_keyboard != mock_new_user.remove_photos_keyboard
            result = self.body(
                mock_new_user=mock_new_user,
                photo_s=photo_s,
                media_group_id='1',
            )
            mock_new_user.is_reply_on_photo.acow(media_group_id='1', )
            assert result == RegConstants.PHOTO_ADDED_SUCCESS

    @staticmethod
    def test_is_reply_on_photo(new_user_f: INewUser, ):
        # Compare with itself
        assert new_user_f.is_reply_on_photo(media_group_id=new_user_f._old_media_group_id) is True
        assert new_user_f.is_reply_on_photo(media_group_id='500') is True
        assert new_user_f.is_reply_on_photo(media_group_id='500') is False
        assert new_user_f.is_reply_on_photo(media_group_id=None) is True
        assert new_user_f.is_reply_on_photo(media_group_id=None) is True
        assert new_user_f.is_reply_on_photo(media_group_id='500') is True
        assert new_user_f._old_media_group_id == '500'  # Assignment every call, just a one check

    @staticmethod
    def test_remove_uploaded_photos(mock_new_user: MagicMock, ):
        with patch_object(target=TGNewUser, attribute='remove_uploaded_photos', ) as mock_remove_uploaded_photos:
            result = NewUser.remove_uploaded_photos(self=mock_new_user, )
        mock_remove_uploaded_photos.acow(mock_new_user, )
        assert mock_new_user._old_media_group_id is None
        assert mock_new_user.current_keyboard == mock_new_user.original_photo_keyboard
        assert result == mock_remove_uploaded_photos.return_value

    @staticmethod
    def test_convert_tg_photo(photo_s: list[PhotoSize], ):
        result = NewUser.convert_tg_photo(photo=photo_s)
        assert result == photo_s[-1].file_id
