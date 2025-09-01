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

from pytest import mark as pytest_mark, raises as pytest_raises, fixture as pytest_fixture
from app.entities.shared.exceptions import PostNotFound

from app.tg.ptb import actions

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest_fixture(scope='function', )
def patched_logger() -> MagicMock:
    with patch_object(target=actions, attribute='known_exceptions_logger', ) as result:
        yield result


class TestAcceptUserHandler:
    """test_accept_user_handler"""

    @staticmethod
    @pytest_fixture(scope='function', )
    def patched_accept_user() -> MagicMock:
        with patch_object(target=actions, attribute='custom_accept_user', ) as result:
            yield result

    @staticmethod
    async def test_incorrect(mock_update: MagicMock, mock_context: MagicMock, patched_accept_user: MagicMock, ):
        """accept_user_handler"""
        patched_accept_user.return_value = None
        # Execution
        result = await actions.extract_passed_user(update=mock_update, context=mock_context, )
        # Checks
        patched_accept_user.acow(app=mock_context.application, message=mock_update.message, )
        mock_context.view.warn.incorrect_user.acow()
        assert len(mock_context.view.mock_calls) == 1
        assert result is None

    @staticmethod
    async def test_correct(mock_update: MagicMock, mock_context: MagicMock, patched_accept_user: MagicMock, ):
        """accept_user_handler"""
        # Execution
        result = await actions.extract_passed_user(update=mock_update, context=mock_context, )
        # Checks
        mock_context.view.warn.incorrect_user.assert_not_called()
        assert len(mock_context.view.mock_calls) == 0
        assert result == patched_accept_user.return_value


class TestCheckIsCollectionsChosen:
    """test_check_is_collections_chosen"""

    @staticmethod
    async def test_chosen(mock_context: MagicMock, ):
        mock_context.user_data.tmp_data.collections_to_share.ids = {1, }
        # Execution
        result = await actions.check_is_collections_chosen(context=mock_context, )
        # Checks
        mock_context.view.collections.collections_to_share_not_chosen.assert_not_called()
        assert len(mock_context.view.mock_calls) == 0
        assert result is True

    @staticmethod
    async def test_not_chosen(mock_context: MagicMock, ):
        mock_context.user_data.tmp_data.collections_to_share.ids = {}
        # Execution
        result = await actions.check_is_collections_chosen(context=mock_context, )
        # Checks
        mock_context.view.collections.collections_to_share_not_chosen.acow(
            reply_to_message_id=mock_context.user_data.tmp_data.collections_to_share.message_id_with_collections
        )
        assert len(mock_context.view.mock_calls) == 1
        assert result is False


class TestCallbackToPostHandler:
    @staticmethod
    async def test_error(mock_update: MagicMock, mock_context: MagicMock, ):
        mock_update.callback_query.data = f'foo _ 1'
        with pytest_raises(actions.UnknownPostType, ):
            await actions.callback_to_post(update=mock_update, context=mock_context, )

    @staticmethod
    @pytest_mark.parametrize(
        argnames='cls, pattern',
        argvalues=(
                (actions.PersonalPost, actions.VoteCbks.PERSONAL_VOTE),
                (actions.BotPublicPost, actions.VoteCbks.PUBLIC_VOTE),
                (actions.ChannelPublicPost, actions.VoteCbks.CHANNEL_PUBLIC_VOTE),
        ), )
    async def test_not_found(
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_logger: MagicMock,
            cls: Type[actions.PersonalPost | actions.BotPublicPost | actions.ChannelPublicPost],
            pattern: str,
    ):
        mock_update.callback_query.data = f'{pattern} _ 1'
        with patch_object(target=cls, attribute='from_callback', return_value=None, ) as mock_from_callback:
            result = await actions.callback_to_post(update=mock_update, context=mock_context, )
        mock_from_callback.acow(callback=mock_update.callback_query, connection=mock_context.connection, )
        patched_logger.info.acow(
            msg=f'{PostNotFound(post=mock_from_callback.return_value, )} - cbk_data: {mock_update.callback_query.data}',
            exc_info=True,
        )
        mock_context.view.posts.post_to_vote_not_found.acow(
            tooltip=mock_update.callback_query,
        )
        assert result is None

    @staticmethod
    @pytest_mark.parametrize(
        argnames='cls, pattern',
        argvalues=(
                (actions.PersonalPost, actions.VoteCbks.PERSONAL_VOTE),
                (actions.BotPublicPost, actions.VoteCbks.PUBLIC_VOTE),
                (actions.ChannelPublicPost, actions.VoteCbks.CHANNEL_PUBLIC_VOTE),
        ), )
    async def test_success(mock_update: MagicMock, mock_context: MagicMock, cls: Type, pattern: str, ):
        mock_update.callback_query.data = f'{pattern} _ 1'
        with patch_object(cls, 'from_callback', ) as mock_from_callback:
            result = await actions.callback_to_post(update=mock_update, context=mock_context, )
        mock_from_callback.acow(callback=mock_update.callback_query, connection=mock_context.connection, )
        assert result == mock_from_callback.return_value
