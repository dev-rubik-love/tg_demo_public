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

from app.entities.user.texts import Reg as RegTexts
from app.tg.entities.user.form import NewUser as NewUserForm

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestNewUser:

    @staticmethod
    def test_remove_uploaded_photos(mock_tg_new_user: MagicMock, ):
        for flag, text in (
                (True, RegTexts.PHOTOS_REMOVED_SUCCESS),
                (False, RegTexts.NO_PHOTOS_TO_REMOVE,),
        ):
            mock_tg_new_user.remove_photos.return_value = flag
            result = NewUserForm.remove_uploaded_photos(self=mock_tg_new_user, )
            mock_tg_new_user.remove_photos.acow()
            assert result == text
            mock_tg_new_user.reset_mock()
