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

from pytest import mark, fixture

from telegram.error import TelegramError

from rubik_core.entities.match.model import Matcher as AppMatcherModel

from app.tg.ptb.entities.user import model
from app.tg.ptb.entities.match.model import Matcher

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from rubik_core.entities.match.structures import Covote
    from app.tg.ptb.entities.user.model import IUser


class TestUser:

    # TODO patch globally during the tests
    @staticmethod
    @fixture(scope='function', autouse=True, )
    def patched_user_bot():
        with patch_object(target=model.User, attribute='bot', ) as mock_bot:
            yield mock_bot

    class TestCheckIsTgActive:
        """test_check_is_tg_active"""

        @staticmethod
        async def test_regular(user_f: IUser, ):
            """
            Test regular behavior (without cache).
            Using class is trouble cuz of alru decorator.
            """
            getattr(user_f.is_tg_active, 'cache_clear', lambda: None)()  # clear cache
            result = await user_f.check_is_tg_active()
            user_f.bot.get_chat.acow(user_f.id, read_timeout=2, )
            assert user_f.is_tg_active == result
            assert result is True

        @staticmethod
        @mark.skip(reason='Cache disabled currently')
        async def test_cache(user_f: IUser, ):
            """
            Test set and get cache.
            Using class is trouble cuz of alru decorator.
            """
            # Ensure cache
            await user_f.check_is_tg_active()
            user_f.bot.reset_mock()  # Keep cache but clear mock calls
            result = await user_f.check_is_tg_active()
            # Only one call during cache setting
            user_f.bot.get_chat.assert_not_called()  # Cache trigger success
            assert user_f.is_tg_active == result
            assert result is True

        @staticmethod
        async def test_exception(user_f: IUser, ):
            """Using class is trouble cuz of alru decorator"""
            getattr(user_f.is_tg_active, 'cache_clear', lambda: None)()  # clear cache
            user_f.bot.get_chat.side_effect = TelegramError('')
            result = await user_f.check_is_tg_active()
            user_f.bot.get_chat.acow(user_f.id, read_timeout=2, )
            assert user_f.is_tg_active == result
            assert result is False
