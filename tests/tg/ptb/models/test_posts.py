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
from typing import TYPE_CHECKING, Any as typing_Any, Callable

from app.tg.ptb.entities.post import model as posts

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import CallbackQuery


class TestPostBase:

    class TestFromCallback:
        """test_from_callback"""

        @staticmethod
        def test_success(callback_fabric_s: Callable[..., CallbackQuery], ):
            callback = callback_fabric_s(data='1', )
            # create=True - Set read method dynamically cuz it not exist for PostBase (can't be used with autospec)
            with patch_object(posts.Shared, 'read', create=True, return_value=None, ) as mock_read:
                result = posts.Shared.from_callback(callback=callback, connection=typing_Any, )
            mock_read.acow(post_id=1, connection=typing_Any, )
            assert result == mock_read.return_value


class TestChannelPublicPost:
    """Test the ChannelPublicPost class."""

    @staticmethod
    def test_read():
        with patch_object(target=posts.tg_post.PublicPost, attribute='read', ) as mock_super_read:
            result = posts.ChannelPublicPost.read(post_id=1, connection=typing_Any, )
        mock_super_read.acow(post_id=1, connection=typing_Any, )
        mock_super_read.return_value.CRUD.read_public_post_channel_message_id(post_id=1, connection=typing_Any, )
        assert result == mock_super_read.return_value

    @staticmethod
    async def test_publish(mock_channel_public_post: MagicMock, ):
        posts.ChannelPublicPost.publish(self=mock_channel_public_post, )
        mock_channel_public_post.update_status.acow(
            status=mock_channel_public_post.Status.RELEASED,
        )
        mock_channel_public_post.CRUD.update_posts_channel_message_id.acow(
            post_id=mock_channel_public_post.id,
            message_id=mock_channel_public_post.posts_channel_message_id,
            connection=mock_channel_public_post.author.connection,
        )

    @staticmethod
    async def test_unpublish(mock_channel_public_post: MagicMock, ):
        mock_channel_public_post.status = mock_channel_public_post.Status.RELEASED
        posts.ChannelPublicPost.unpublish(self=mock_channel_public_post, )
        mock_channel_public_post.CRUD.update_posts_channel_message_id.acow(
            post_id=mock_channel_public_post.id,
            message_id=None,
            connection=mock_channel_public_post.author.connection,
        )
        mock_channel_public_post.update_status.acow(status=mock_channel_public_post.Status.READY_TO_RELEASE, )
