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
from typing import Callable, TYPE_CHECKING

import pytest

from app.tg.ptb.entities.vote.constants import Cbks
from app.tg.ptb.entities.vote import handlers_definition

from tests.tg.ptb.triggers.conftest import check_is_all_mock_handlers_called, cancel_body
from tests.tg.ptb.conftest import get_text_cases


if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import Application


@pytest.fixture(scope='module', autouse=True, )
def check_is_all_called():
    """Internal test to check that all handlers was called"""
    gen = check_is_all_mock_handlers_called(handlers=(handlers_definition.available_handlers,))
    next(gen, )  # Executes before tests
    yield
    next(gen, None)  # Executes after all the tests. none to prevent StopIteration


class TestPublicVoteCbkHandler:
    @staticmethod
    @pytest.mark.parametrize(
        argnames='cbk_data', argvalues=[
            *get_text_cases(texts=[Cbks.PUBLIC_VOTE], lower=False),
            *get_text_cases(texts=['foo', 'bar egg'])
        ]
    )
    async def test_buttons_not_triggered(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            cbk_data: str,
    ):
        update = update_fabric_s(callback_kwargs={'data': cbk_data, }, )
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.accept_public_vote_cbk.callback.assert_not_called()

    @staticmethod
    async def test_buttons_triggered(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(callback_kwargs={'data': Cbks.PUBLIC_VOTE, }, )
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.accept_public_vote_cbk.callback.assert_called_once()


class TestPersonalVoteCbkHandler:

    @staticmethod
    @pytest.mark.parametrize(
        argnames='cbk_data', argvalues=[
            *get_text_cases(texts=[Cbks.PERSONAL_VOTE], lower=False, ),
            *get_text_cases(texts=['foo', 'bar egg'], )
        ], )
    async def test_buttons_not_triggered(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            cbk_data: str,
    ):
        update = update_fabric_s(callback_kwargs={'data': cbk_data, }, )
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.accept_personal_vote_cbk.callback.assert_not_called()

    @staticmethod
    async def test_buttons_triggered(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(callback_kwargs={'data': Cbks.PERSONAL_VOTE, }, )
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.accept_personal_vote_cbk.callback.assert_called_once()


async def test_channel_public_vote_cbk_handler(
        update_fabric_s: Callable[..., Update],
        app_s_with_mock_handlers: Application,
):
    """test triggered"""
    update = update_fabric_s(callback_kwargs={'data': Cbks.CHANNEL_PUBLIC_VOTE, }, )
    await app_s_with_mock_handlers.process_update(update=update, )
    handlers_definition.accept_channel_public_vote_cbk.callback.assert_called_once()
