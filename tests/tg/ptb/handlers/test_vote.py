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

from pytest import fixture as pytest_fixture, mark as pytest_mark, skip as pytest_skip

from rubik_core.entities.vote.base import Value, VotableValue
from rubik_core.entities.vote.model import HandledVote

from app.tg.ptb.entities.vote import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import Update


@pytest_fixture(scope='function', )
def patched_actions_callback_to_post() -> MagicMock:
    with patch_object(target=handlers, attribute='actions_callback_to_post', ) as mock_callback_to_post:
        yield mock_callback_to_post


@pytest_fixture(scope='function', )
def patched_public_vote_cls() -> MagicMock:
    with patch_object(handlers, 'PublicVote', ) as mock_vote_cls:
        yield mock_vote_cls


@pytest_fixture(scope='function', )
def patched_get_answer_text() -> MagicMock:
    """Mock comparing fails on real object"""
    with patch_object(target=handlers, attribute='get_answer_text', ) as result:
        yield result


def test_get_answer_text():
    """Indeed view responsibility but vote view has too few functionality for separate file currently"""
    handled_vote = HandledVote(incoming_value=VotableValue(1), old_value=Value(0), )
    assert handlers.get_answer_text(handled_vote=handled_vote, ) == handlers.texts.SUCCESS_VOTE_POSITIVE
    handled_vote = HandledVote(incoming_value=VotableValue(1), old_value=Value(-1), )
    assert handlers.get_answer_text(handled_vote=handled_vote, ) == handlers.texts.SUCCESS_VOTE_ZERO
    handled_vote = HandledVote(incoming_value=VotableValue(-1), old_value=Value(0), )
    assert handlers.get_answer_text(handled_vote=handled_vote, ) == handlers.texts.SUCCESS_VOTE_NEGATIVE
    handled_vote = HandledVote(incoming_value=VotableValue(1), old_value=Value(1), )
    assert handlers.get_answer_text(handled_vote=handled_vote, ) == handlers.texts.VOTE_ALREADY_SET_POSITIVE
    handled_vote = HandledVote(incoming_value=VotableValue(-1), old_value=Value(-1), )
    assert handlers.get_answer_text(handled_vote=handled_vote, ) == handlers.texts.VOTE_ALREADY_SET_NEGATIVE


class TestPublicVoteCbkHandler:
    """public_vote_cbk_handler"""

    @staticmethod
    @pytest_mark.parametrize("error", [Exception(), handlers.UnknownPostType()])
    async def test_not_found(
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_logger: MagicMock,
            error: Exception,
    ):
        patched_actions_callback_to_post.side_effect = error
        # execution
        await handlers.public_vote_cbk_handler(update=mock_update, context=mock_context, )
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        patched_logger.error.acow(msg=error, exc_info=True, )
        mock_context.view.posts.voting_internal_error.acow(
            tooltip=mock_update.callback_query,
        )
        mock_context.user.set_vote.assert_not_called()

    @staticmethod
    async def test_declined(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_public_vote_cls: MagicMock,
            patched_get_answer_text: MagicMock,
    ):
        mock_context.user.set_vote.return_value.is_accepted = False
        # Execution
        await handlers.public_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            vote=patched_public_vote_cls.from_callback.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        patched_get_answer_text.assert_called_once_with(handled_vote=mock_context.user.set_vote.return_value, )

    @staticmethod
    async def test_accepted(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_public_vote_cls: MagicMock,
            patched_get_answer_text: MagicMock,
    ):
        mock_context.user.set_vote.return_value.is_accepted = True
        # Execution
        await handlers.public_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            post=patched_actions_callback_to_post.return_value,
            vote=patched_public_vote_cls.from_callback.return_value,
        )
        patched_get_answer_text.acow(handled_vote=mock_context.user.set_vote.return_value, )
        pytest_skip('dispatcher no more exists in PTB')
        mock_context.dispatcher.run_async.acow(
            func=patched_actions_callback_to_post.return_value.update_votes_mass_job,
        )


class TestChannelPublicVoteCbkHandler:
    """channel_public_vote_cbk_handler"""

    @staticmethod
    @pytest_mark.parametrize("error", [Exception(), handlers.UnknownPostType()])
    async def test_not_found(
            mock_update: MagicMock,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_logger: MagicMock,
            error: Exception,
    ):
        patched_actions_callback_to_post.side_effect = error
        # Execution
        await handlers.channel_public_vote_cbk_handler(update=mock_update, context=mock_context, )
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        patched_logger.error.acow(msg=error, exc_info=True, )
        mock_context.view.posts.voting_internal_error.acow(
            tooltip=mock_update.callback_query,
        )
        mock_context.user.set_vote.assert_not_called()
        pytest_skip('dispatcher no more exists in PTB')
        mock_context.dispatcher.run_async.assert_not_called()

    @staticmethod
    async def test_declined(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_public_vote_cls: MagicMock,
            patched_get_answer_text: MagicMock,
    ):
        mock_context.user.set_vote.return_value.is_accepted = False
        # Execution
        await handlers.channel_public_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            vote=patched_public_vote_cls.from_callback.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        patched_actions_callback_to_post.return_value.update_poll_keyboard.assert_not_called()
        patched_get_answer_text.acow(handled_vote=mock_context.user.set_vote.return_value, )

    @staticmethod
    async def test_accepted(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_public_vote_cls: MagicMock,
            patched_get_answer_text: MagicMock,
    ):
        mock_context.user.set_vote.return_value.is_accepted = True
        # Execution
        await handlers.channel_public_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            vote=patched_public_vote_cls.from_callback.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        mock_context.view.posts.channel_public_post.update_poll_keyboard.acow(
            post=patched_actions_callback_to_post.return_value,
            message_id=mock_update.callback_query.message.message_id,
        )
        patched_get_answer_text.acow(handled_vote=mock_context.user.set_vote.return_value, )


class TestPersonalVoteCbkHandler:
    """personal_vote_cbk_handler"""

    @staticmethod
    @pytest_fixture(scope='function', )
    def patched_personal_vote_cls() -> MagicMock:
        with patch_object(handlers, 'PersonalVote', ) as mock_vote_cls:
            yield mock_vote_cls

    @staticmethod
    @pytest_mark.parametrize("error", [Exception(), handlers.UnknownPostType()])
    async def test_voting_internal_error(
            mock_update: Update,
            mock_context: MagicMock,
            patched_personal_vote_cls: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_logger: MagicMock,
            error: Exception,
    ):
        mock_update.callback_query.data = f'_ 1 +1'  # Any number
        patched_actions_callback_to_post.side_effect = error
        # Execution
        await handlers.personal_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        patched_logger.error.acow(msg=error, exc_info=True, )
        mock_context.view.posts.voting_internal_error.acow(
            tooltip=mock_update.callback_query,
        )

    @staticmethod
    async def test_post_not_found(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_personal_vote_cls: MagicMock,
    ):
        mock_update.callback_query.data = f'_ 1 +1'  # Any number
        # Execution
        await handlers.personal_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_personal_vote_cls.from_callback.acow(
            user=mock_context.user,
            callback=mock_update.callback_query,
        )
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )

    @staticmethod
    @pytest_mark.parametrize(argnames='post_id', argvalues=['+1', '-1'])
    async def test_declined(
            mock_update: Update,
            mock_context: MagicMock,
            patched_personal_vote_cls,
            patched_actions_callback_to_post: MagicMock,
            patched_get_answer_text: MagicMock,
            post_id: str,
    ):
        mock_context.user.set_vote.return_value.is_accepted = False
        mock_update.callback_query.data = f'_ 2 {post_id}'  # "2" is opposite_id, post_id is any number
        # Execution
        await handlers.personal_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_personal_vote_cls.from_callback.acow(
            user=mock_context.user,
            callback=mock_update.callback_query,
        )
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            vote=patched_personal_vote_cls.from_callback.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        patched_actions_callback_to_post.return_value.update_poll_keyboard.assert_not_called()
        patched_get_answer_text.acow(handled_vote=mock_context.user.set_vote.return_value, )

    @staticmethod
    @pytest_mark.parametrize(argnames='post_id', argvalues=['+1', '-1'])
    async def test_accepted(
            mock_update: Update,
            mock_context: MagicMock,
            patched_actions_callback_to_post: MagicMock,
            patched_personal_vote_cls: MagicMock,
            patched_get_answer_text: MagicMock,
            post_id: str,
    ):
        mock_user = patched_personal_vote_cls.User.return_value
        mock_update.callback_query.data = f'_ 2 {post_id}'  # "2" is opposite_id, post_id is any number
        mock_context.user.set_vote.return_value.is_accepted = True
        # Execution
        await handlers.personal_vote_cbk_handler(update=mock_update, context=mock_context, )
        # Checks
        patched_personal_vote_cls.from_callback.acow(
            user=mock_context.user,
            callback=mock_update.callback_query,
        )
        patched_actions_callback_to_post.acow(update=mock_update, context=mock_context, )
        mock_context.user.set_vote.acow(
            vote=patched_personal_vote_cls.from_callback.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        patched_personal_vote_cls.User.acow(id=2, connection=mock_context.connection, )
        patched_personal_vote_cls.get_user_vote.acow(
            user=patched_personal_vote_cls.User.return_value,
            post=patched_actions_callback_to_post.return_value,
        )
        mock_context.view.posts.personal.update_poll_keyboard.acow(
            post=patched_actions_callback_to_post.return_value,
            clicker_vote=patched_personal_vote_cls.from_callback.return_value,
            opposite_vote=patched_personal_vote_cls.get_user_vote.return_value,
            keyboard=mock_update.effective_message.reply_markup,
        )
        patched_get_answer_text.acow(handled_vote=mock_context.user.set_vote.return_value, )
