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
from unittest.mock import ANY

import pytest
from telegram.constants import ChatAction

from app.tg.ptb.entities.mix import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import Update


@pytest.fixture(scope='function', )
def patched_db() -> MagicMock:
    orig_connection_pool = handlers.Postgres.create_connection_pool()  # Save orig value for specs cuz will be patched
    with patch_object(target=handlers, attribute='Postgres', ) as mock_db:
        mock_db.connection_pool.mock_add_spec(spec=orig_connection_pool, )  # Replace None specs
        yield mock_db


async def test_pickle_persistence_flush_handler(mock_context: MagicMock, ):
    await handlers.pickle_persistence_flush_handler(_=typing_Any, context=mock_context, )
    mock_context.application.persistence.flush.acow()
    mock_context.view.say_ok.acow()


async def test_hide(mock_update: MagicMock, mock_context: MagicMock, ):
    mock_update.callback_query.data = '_ 1 2'
    await handlers.hide(update=mock_update, context=mock_context, )
    message_ids = [int(message_id) for message_id in ('1', '2')]
    mock_context.view.mix.drop_hide_btn.acow(message_ids=message_ids, )


async def test_unknown_handler(mock_update: MagicMock, mock_context: MagicMock, ):
    await handlers.unknown_handler(update=mock_update, context=mock_context, )
    mock_context.view.mix.unknown_handler.acow(
        reply_to_message_id=mock_update.effective_message.message_id,
    )


async def test_typing_response(mock_update: MagicMock, mock_context: MagicMock, patched_logger: MagicMock, ):
    mock_context.bot.send_chat_action.side_effect = Exception
    await handlers.typing_response(update=mock_update, context=mock_context, )
    mock_context.bot.send_chat_action.acow(chat_id=mock_update.effective_chat.id, action=ChatAction.TYPING, )
    patched_logger.error.acow(msg=ANY, exc_info=True, )


async def test_faq(mock_context: MagicMock, ):
    await handlers.faq(_=typing_Any, context=mock_context, )
    mock_context.view.mix.faq.acow()


async def test_health(mock_context: MagicMock, ):
    await handlers.health(_=typing_Any, context=mock_context, )
    mock_context.view.say_ok.acow()


async def test_donate(mock_context: MagicMock, ):
    await handlers.donate(_=typing_Any, context=mock_context, )
    mock_context.view.mix.donate.acow()


async def test_all_bot_commands_handler_handler(mock_context: MagicMock, ):
    await handlers.all_bot_commands_handler(_=typing_Any, context=mock_context, )
    mock_context.view.mix.show_bot_commands.acow()


async def test_debug_logger(mock_context: MagicMock, mock_update: Update, patched_logger: MagicMock, ):
    mock_update.effective_message.text = 'Test text'
    mock_update.effective_message.effective_attachment = 'Test attachment'
    mock_update.callback_query.data = 'Test data'
    mock_context.user_data = {'Test user data': 'Test user value'}
    mock_context.chat_data = {'Test chat data': 'Test chat value'}
    mock_context.bot_data = {'Test bot data': 'Test bot value'}
    await handlers.debug_logger(update=mock_update, context=mock_context, )
    expected_log_data = {
        "message_text": 'Test text',
        "message_attachment": 'Test attachment',
        "callback_data": 'Test data',
        "user_data": {'Test user data': 'Test user value'},
        "chat_data": {'Test chat data': 'Test chat value'},
        "bot_data": {'Test bot data': 'Test bot value'},
    }
    expected_arg = '\n' + handlers.pprint_pformat(expected_log_data)
    patched_logger.debug.acow(expected_arg)


class TestGenBotsHandlerCmd:
    """create_bots_handler_cmd"""

    @staticmethod
    async def test_get_num_from_text_raises_value_error(mock_update: MagicMock, mock_context: MagicMock, ):
        with (
            patch_object(handlers, 'get_num_from_text', return_value=None, ) as mock_get_num_from_text,
            patch_object(handlers, 'limit_num', ) as mock_limit_num,
        ):
            await handlers.gen_bots_handler_cmd(update=mock_update, context=mock_context, )
            mock_get_num_from_text.acow(text=mock_update.effective_message.text, )
            mock_context.view.warn.nan_help_msg.acow()
            mock_limit_num.assert_not_called()

    @staticmethod
    async def test_valid_number_in_message(mock_update: MagicMock, mock_context: MagicMock, ):
        with (
            patch_object(target=handlers, attribute='get_num_from_text', ) as mock_get_num_from_text,
            patch_object(target=handlers, attribute='limit_num', return_value=5, ) as mock_limit_num,
            patch_object(target=handlers.SystemService, attribute='create_bots', ) as mock_create_bots,
        ):
            await handlers.gen_bots_handler_cmd(update=mock_update, context=mock_context)
            mock_get_num_from_text.acow(text=mock_update.effective_message.text, )
            mock_limit_num.acow(num=mock_get_num_from_text.return_value, min_num=1, max_num=99, )
            mock_create_bots.acow(bots_ids=list(range(1, mock_limit_num.return_value + 1)), )
            mock_context.view.say_ok.acow()


async def test_gen_me_handler_cmd(
        mock_update: MagicMock,
        mock_context: MagicMock,
        mock_collection: MagicMock,
):
    mock_collection.get_posts.return_value = (typing_Any,)
    with (
        patch_object(target=handlers, attribute='SystemService', ) as MockSystemService,
        patch_object(
            target=handlers.CollectionService,
            attribute='get_defaults',
            return_value=(mock_collection,),
        ) as mock_get_defaults,
    ):
        await handlers.gen_me_handler_cmd(update=mock_update, context=mock_context, )
    MockSystemService.create_bots.acow(bots_ids=[mock_update.effective_user.id, ], )
    mock_get_defaults.acow(prefix=handlers.CollectionService.NamePrefix.PUBLIC, )
    mock_collection.get_posts.assert_called_with(
        collection_id=mock_collection.id,
        connection=mock_context.connection,
    )
    MockSystemService.generator.gen_vote.acow(
        user=mock_context.user,
        post=typing_Any,
    )
    mock_context.user.set_vote.acow(
        vote=MockSystemService.generator.gen_vote.return_value,
        post=typing_Any,
    )
    mock_context.view.say_ok.acow()


class TestError:
    """error_handler"""

    @staticmethod
    async def test_error_regular(mock_context: MagicMock, mock_update: MagicMock, patched_logger: MagicMock, ):
        mock_context.error = ZeroDivisionError()  # Any unexpected error is ok
        mock_update.inline_query = mock_update.callback_query = None
        await handlers.error_handler(update=mock_update, context=mock_context, )
        mock_context.view.internal_error.acow()
        patched_logger.error.acow(msg=ANY, exc_info=mock_context.error, )

    @staticmethod
    async def test_error_cbk(mock_context: MagicMock, mock_update: MagicMock, patched_logger: MagicMock, ):
        mock_update.inline_query = None
        mock_context.error = Exception()  # Any unknown error is ok
        await handlers.error_handler(update=mock_update, context=mock_context, )
        mock_context.view.internal_error.acow(tooltip=mock_update.callback_query, )
        patched_logger.error.acow(msg=ANY, exc_info=mock_context.error, )


class TestAnalyticsHandler:
    """test_analytics_handler"""

    @staticmethod
    async def test_success(mock_update: MagicMock, ):
        mock_update.effective_message.text = 'Test text'
        with patch_object(handlers.httpx_client, 'post', ) as mock_post:
            await handlers.analytics_handler(update=mock_update, _=typing_Any)
        mock_post.acow(
            url="https://api.graspil.ru/api/send-batch-update",
            headers={
                'Content-Type': 'application/json',
                'Api-Key': handlers.GRASPIL_ANALYTICS_API_KEY,
            },
            json=[
                {
                    "date": ANY,
                    "update": mock_update.to_dict.return_value,
                },
            ],
        )

    @staticmethod
    async def test_fatal_error(mock_update: MagicMock, patched_logger: MagicMock, ):
        mock_update.effective_message.text = 'Test text'
        with patch_object(
                target=handlers.httpx_client,
                attribute='post',
                side_effect=ZeroDivisionError(''),
        ):
            await handlers.analytics_handler(update=mock_update, _=typing_Any)
        patched_logger.error.acow(msg=ANY, exc_info=True, )

    @staticmethod
    async def test_connection_error(mock_update: MagicMock, patched_logger: MagicMock, ):
        mock_update.effective_message.text = 'Test text'
        with (
            patch_object(target=handlers, attribute='graspil_logger', ) as mock_graspil_logger,
            patch_object(
                target=handlers.httpx_client,
                attribute='post',
                side_effect=handlers.ConnectTimeout(message=''),
            ),
        ):
            await handlers.analytics_handler(update=mock_update, _=typing_Any)
        mock_graspil_logger.error.acow(msg=ANY, exc_info=False, )


class TestReleaseResources:
    """ test_release_resources """

    @staticmethod
    async def test_release_resources_regular_conn(mock_context: MagicMock, patched_db: MagicMock, ):
        mock_context.user_data.forms.target = None
        orig_connection = mock_context.connection
        await handlers.release_resources(_=typing_Any, context=mock_context, )
        patched_db.connection_pool.putconn.acow(conn=orig_connection, )
        assert mock_context.connection is None

    @staticmethod
    async def test_release_resources_pool_conn(mock_context: MagicMock, patched_db: MagicMock, ):
        mock_context.user_data.forms.target = None
        orig_connection = mock_context.connection.value
        mock_context.connection.mock_add_spec(spec=handlers.LazyValue(get_value_func=lambda: None, ), )
        await handlers.release_resources(_=typing_Any, context=mock_context, )
        patched_db.connection_pool.putconn.acow(conn=orig_connection, )
        assert mock_context.connection is None

    @staticmethod
    async def test_exception(mock_context: MagicMock, patched_logger: MagicMock, patched_db: MagicMock, ):
        mock_context.user_data.forms.target = None
        patched_db.connection_pool.putconn.side_effect = Exception()
        await handlers.release_resources(_=typing_Any, context=mock_context, )
        patched_logger.error.acow(msg=ANY, exc_info=True, )
