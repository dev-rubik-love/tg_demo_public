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
from telegram import (
    Update as Update,
    Location,
    PhotoSize,
)
from telegram.ext import Application

from rubik_core.generation import generator
from app.tg.ptb.entities.user.constants import REG_S
from app.tg.ptb.entities.user import handlers_definition
from app.tg.ptb.entities.user.texts import Reg as RegConstants

from tests.tg.ptb.triggers.conftest import check_is_all_mock_handlers_called, cancel_body
from tests.tg.ptb.conftest import get_text_cases

if TYPE_CHECKING:
    pass


@pytest.fixture(scope='module', autouse=True, )
def check_is_all_called(request):
    """Internal test to check that all handlers was called"""
    gen = check_is_all_mock_handlers_called(handlers=(handlers_definition.available_handlers,))
    next(gen, )  # Executes before tests
    yield
    next(gen, None)  # Executes after all the tests. none to prevent StopIteration


class TestRegistration:
    @staticmethod
    async def test_reg_entry_point(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs={'cmd_text': REG_S, }, )
        assert (
                (update.effective_chat.id, update.effective_user.id) not in
                handlers_definition.RegistrationCH.CH._conversations
        )
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.entry_point.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_reg_entry_point_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        handlers_definition.RegistrationCH.entry_point_handler.callback.reset_mock()
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 0
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.entry_point_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(
        argnames='text',
        argvalues=get_text_cases(texts=[generator.gen_fullname()]),
    )
    async def test_user_name_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.name_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 1
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.name_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=RegConstants.REG_GOALS))
    async def test_user_goal_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.goal_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 2
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.goal_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=RegConstants.REG_GENDERS))
    async def test_user_gender_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,

    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.gender_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 3
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.gender_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
    async def test_user_age_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,

    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.age_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 4
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.age_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    async def test_user_location_handler_text(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,

    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.location_handler_text.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 5
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.location_handler_text.callback.assert_called_once()

    @staticmethod
    async def test_user_location_handler_geo(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
    ):
        update = update_fabric_s(message_kwargs={'location': Location(longitude=45, latitude=45), }, )
        handlers_definition.RegistrationCH.location_handler_geo.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 5
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.location_handler_geo.callback.assert_called_once()

    @staticmethod
    async def test_user_photos_handler_tg_photo(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            photo_s: list[PhotoSize],

    ):
        update = update_fabric_s(message_kwargs={'photo': photo_s, }, )
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 6
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.photos_handler_photo.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='media_group_id', argvalues=['1', '2'])
    async def test_user_photos_handler_album(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            media_group_id: str,
            photo_s: list[PhotoSize],

    ):
        update = update_fabric_s(message_kwargs={'photo': photo_s, 'media_group_id': media_group_id, }, )
        handlers_definition.RegistrationCH.photos_handler_photo.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 6
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.photos_handler_photo.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(
        argnames='text',
        argvalues=[RegConstants.Buttons.USE_ACCOUNT_PHOTOS, RegConstants.Buttons.REMOVE_PHOTOS],
    )
    async def test_user_photos_handler_text(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.photos_handler_text.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 6
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.photos_handler_text.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(
        argnames='text',
        argvalues=get_text_cases(texts=[generator.gen_comment() for _ in range(5)], )
    )
    async def test_user_comment_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.comment_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 7
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.comment_handler.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[RegConstants.FINISH_KEYWORD], ))
    async def test_user_confirm_handler(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            text: str,
    ):
        update = update_fabric_s(message_kwargs={'text': text, }, )
        handlers_definition.RegistrationCH.confirm_handler.callback.reset_mock()
        handlers_definition.RegistrationCH.CH._conversations[(update.effective_chat.id, update.effective_user.id)] = 8
        await app_s_with_mock_handlers.process_update(update=update, )
        handlers_definition.RegistrationCH.confirm_handler.callback.assert_called_once()

    @staticmethod
    async def test_cancel(
            update_fabric_s: Callable[..., Update],
            app_s_with_mock_handlers: Application,
            monkeypatch,
    ):
        await cancel_body(
            update_fabric=update_fabric_s,
            ptb_app=app_s_with_mock_handlers,
            ch=handlers_definition.RegistrationCH.CH,
            callback=handlers_definition.RegistrationCH.cancel_handler.callback,
            monkeypatch=monkeypatch,
        )
