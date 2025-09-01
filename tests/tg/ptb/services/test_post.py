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

from pytest import mark as pytest_mark, fixture as pytest_fixture
from telegram.error import TelegramError
from app.tg.ptb.entities.post import services

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest_fixture(scope='function', )
def patched_logger() -> MagicMock:
    with patch_object(target=services, attribute='known_exceptions_logger', ) as result:
        yield result


class TestBotPublicPost:

    @staticmethod
    def test_get_voted_users(mock_bot_public_post: MagicMock, ):
        result = services.BotPublicPost.get_voted_users(post=mock_bot_public_post, )
        mock_bot_public_post.get_voted_users.acow(
            connection=services.BotPublicPost.System.user.connection
        )
        assert result == mock_bot_public_post.get_voted_users.return_value


@pytest_mark.skip(reason='No in use, need review', )
class TestMassUpdateKeyboardJob:
    """mass_update_keyboard_job"""

    @staticmethod
    async def test_error(mock_bot_public_post: MagicMock, ):
        mock_bot_public_post.update_poll_keyboard.side_effect = TelegramError('')
        with (
            patch_object(
                services.BotPublicPost,
                'get_voted_users',
                return_value=[mock_bot_public_post.author],
            ) as mock_get_voted_users,
            patch_object(
                target=services.BotPublicPost.System.Mapper.PublicVote,
                attribute='read',
            ) as mock_read,
        ):
            result = await services.BotPublicPost.mass_update_keyboard_job(
                bot_post=mock_bot_public_post,
            )
            # Checks
            mock_get_voted_users.acow(post=mock_bot_public_post, )
            mock_read.acow(
                post_id=mock_bot_public_post.post_id,
                user=mock_get_voted_users.return_value[0],
            )
            mock_bot_public_post.update_poll_keyboard.acow(
                clicker_vote=mock_read.return_value,
            )
            assert result == []

    @staticmethod
    async def test_success(mock_bot_public_post: MagicMock, ):
        with (
            patch_object(
                target=services.BotPublicPost,
                attribute='get_voted_users',
                return_value=[mock_bot_public_post.author],
            ) as mock_get_voted_users,
            patch_object(
                target=services.BotPublicPost.System.Mapper.PublicVote,
                attribute='read',
                autospec=True,
            ) as mock_read,
        ):
            result = await services.BotPublicPost.mass_update_keyboard_job(
                bot_post=mock_bot_public_post,
            )
            # Checks
            mock_get_voted_users.acow(post=mock_bot_public_post, )
            mock_read.acow(
                post_id=mock_bot_public_post.post_id,
                user=mock_get_voted_users.return_value[0],
            )
            mock_bot_public_post.update_poll_keyboard.acow(
                clicker_vote=mock_read.return_value,
            )
            assert result == [mock_bot_public_post.update_poll_keyboard.return_value]
