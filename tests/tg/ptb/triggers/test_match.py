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

import pytest
from telegram import Update as Update
from telegram.ext import Application

from app.tg.ptb.entities.match.texts import Search as SearchTexts
from app.tg.ptb.entities.match.model import Matcher
from app.tg.ptb.entities.match import handlers_definition

from tests.tg.ptb.triggers.conftest import check_is_all_mock_handlers_called, cancel_body
from tests.tg.ptb.conftest import get_text_cases

if TYPE_CHECKING:
    pass


@pytest.fixture(scope='module', autouse=True, )
def check_is_all_called():
    """Internal test to check that all handlers was called"""
    gen = check_is_all_mock_handlers_called(handlers=(handlers_definition.available_handlers, ))
    next(gen, )  # Executes before tests
    yield
    next(gen, None)  # Executes after all the tests. none to prevent StopIteration


async def test_personal_example(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    update = update_fabric_s(message_kwargs={'cmd_text': handlers_definition.constants.PERSONAL_EXAMPLE_S}, )
    await app_s_with_mock_handlers.process_update(update=update)
    handlers_definition.personal_example_cmd.callback.assert_called_once()


class TestSearch:
    @staticmethod
    async def test_entry_point(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs={'cmd_text': handlers_definition.constants.SEARCH_S, }, )
        handlers_definition.SearchCH.CH._conversations.pop((update.effective_chat.id, update.effective_user.id), None)
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.entry_point.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_entry_point_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.entry_point_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.entry_point_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize('value', [0, 1])
    async def test_channel_sources_cbk_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            value: int,
    ):
        handlers_definition.SearchCH.checkbox_cbk_handler.callback.reset_mock()
        cbk = f'{handlers_definition.constants.Cbks.CHOOSE_CHANNELS} any text here (.*) {value}'
        update = update_fabric_s(callback_kwargs={'data': cbk}, )
        handlers_definition.SearchCH.channel_sources_cbk_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.channel_sources_cbk_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=SearchTexts.TARGET_GOALS))
    async def test_target_goal_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.goal_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 1
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.goal_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=SearchTexts.TARGET_GENDERS))
    async def test_target_gender_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.gender_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 2
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.gender_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
    async def test_target_age_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.age_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 3
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.age_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='checkbox', argvalues=Matcher.Filters.Checkboxes(), )
    @pytest.mark.parametrize(argnames='value', argvalues=[1, -1])
    async def test_checkbox_cbk_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            checkbox: str,
            value: int,
    ):
        update = update_fabric_s(
            callback_kwargs={'data': f'{handlers_definition.constants.Cbks.CHECKBOX} {checkbox} {value}', },
        )
        handlers_definition.SearchCH.checkbox_cbk_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 4
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.checkbox_cbk_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_target_checkboxes_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.checkboxes_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 4
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.checkboxes_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=SearchTexts.TARGET_SHOW_CHOICE))
    async def test_target_confirm_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.confirm_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 5
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.confirm_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[SearchTexts.Buttons.SHOW_MORE]))
    async def test_target_confirm_handler_show_match(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,

    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.show_match_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 6
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.show_match_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[SearchTexts.COMPLETE_KEYWORD]))
    async def test_target_show_match_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,

    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.SearchCH.show_match_handler.callback.reset_mock()
        handlers_definition.SearchCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 6
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.SearchCH.show_match_handler.callback.assert_called_once()

    @staticmethod
    async def test_cancel(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=handlers_definition.SearchCH.CH,
            callback=handlers_definition.SearchCH.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )


class TestGetStatisticWithHandler:

    @staticmethod
    async def test_entry_point(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs={'cmd_text': handlers_definition.constants.GET_STATISTIC_WITH_S}, )
        await app_s_with_mock_handlers.process_update(update=update)
        handlers_definition.GetStatisticWithCH.entry_point.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=['-1', '+1', 'foo', 'foo bar'])  # users ids
    async def test_entry_point_handler_triggered(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        handlers_definition.GetStatisticWithCH.entry_point_handler.callback.reset_mock()  # Reset for parametrize
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handler = handlers_definition.GetStatisticWithCH.CH
        handler._conversations[(update.effective_chat.id, update.effective_user.id)] = 0
        await app_s_with_mock_handlers.process_update(update=update)
        mock_callback = handlers_definition.GetStatisticWithCH.entry_point_handler.callback
        mock_callback.assert_called_once()
