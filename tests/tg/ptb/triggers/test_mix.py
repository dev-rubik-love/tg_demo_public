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
from typing import TYPE_CHECKING, Callable
from logging import CRITICAL as LOGGING_CRITICAL

import pytest

from app.config import MAIN_ADMIN
from app.tg.ptb.entities.mix import constants, handlers_definition

from tests.tg.ptb.triggers.conftest import check_is_all_mock_handlers_called

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import Application


@pytest.fixture(scope='module', autouse=True, )
def check_is_all_called():
    """Internal test to check that all handlers was called"""
    gen = check_is_all_mock_handlers_called(handlers=handlers_definition.available_handlers.values())
    next(gen, )  # Executes before tests
    yield
    next(gen, None)  # Executes after all the tests. none to prevent StopIteration


@pytest.mark.parametrize(
    argnames='text_kwargs',
    argvalues=(
            {'cmd_text': 'foo'},  # message_kwargs
            {'text': 'foo'},  # message_kwargs
    )
)
async def test_unknown_post_handler(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
        text_kwargs: dict,
):
    update = update_fabric_s(message_kwargs=text_kwargs, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.unknown_bot_handler.callback.assert_called_once()
    handlers_definition.unknown_bot_handler.callback.reset_mock()


async def test_help_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.ALL_BOT_COMMANDS_S}, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.help_handler_cmd.callback.assert_called_once()


async def test_faq_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.FAQ_S}, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.faq_handler_cmd.callback.assert_called_once()


@pytest.mark.parametrize(
    argnames='text_kwargs', argvalues=(
            {'cmd_text': 'foo'},  # message_kwargs
            {'text': 'foo'},  # message_kwargs
    )
)
async def test_typing_response(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
        text_kwargs: dict,
):
    handlers_definition.typing_response.callback.reset_mock()
    update = update_fabric_s(message_kwargs=text_kwargs, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.typing_response.callback.assert_called_once()


async def test_health_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.HEALTH_S}, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.help_handler_cmd.callback.assert_called_once()


async def test_donate_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.DONATE_S}, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.faq_handler_cmd.callback.assert_called_once()


async def test_pickle_persistence_flush_handler_cmd(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': constants.PICKLE_FLUSH_S}, user_kwargs={'id': MAIN_ADMIN, }, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.pickle_persistence_flush_handler_cmd.callback.assert_called_once()


async def test_hide_cbk_handler(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    """test triggered"""
    update = update_fabric_s(callback_kwargs={'data': f'{handlers_definition.constants.HIDE_S} 1', }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.hide_cbk_handler.callback.assert_called_once()


async def test_error_handler(update_s: Update, app_s_with_mock_handlers: Application, caplog, ):
    mock_callback = list(app_s_with_mock_handlers.error_handlers.keys())[0]
    mock_callback.reset_mock()  # To pass tear down checks that error handlers was not called
    caplog.set_level(LOGGING_CRITICAL)  # Suppress logs only during test
    await app_s_with_mock_handlers.process_error(update=update_s, error=ZeroDivisionError(), )
    mock_callback.assert_called_once()  # What if multiple error handlers?


async def test_empty_cbk_handler(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(callback_kwargs={'data': handlers_definition.constants.Cbks.EMPTY, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.empty_cbk_handler.callback.assert_called_once()


async def test_unknown_bot_cbk_handler(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    """
    Will be triggered by any cbk.
    In normal usage will be intercepted by actual handler and before accessing this last resort trigger
    """
    handlers_definition.unknown_bot_cbk_handler.callback.reset_mock()  # Called by hide cbk presumably
    update = update_fabric_s(callback_kwargs={'data': 'qwe', }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.unknown_bot_cbk_handler.callback.assert_called_once()
