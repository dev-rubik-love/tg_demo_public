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
from unittest.mock import ANY
from typing import TYPE_CHECKING

from pytest import mark as pytest_mark

from rubik_core.generation import generator

from app.tg.ptb.entities.user import handlers
from tests.tg.ptb.conftest import get_text_cases
from tests.conftest import patch_object


if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import Update

CLS_TO_TEST = handlers
EXCEPTION = CLS_TO_TEST.IncorrectProfileValue


async def test_reg_entry_point(mock_context: MagicMock, mock_update: Update, ):
    # Execution
    result = await CLS_TO_TEST.entry_point(_=mock_update, context=mock_context, )
    # Checks
    mock_context.view.reg.say_reg_hello.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 0


async def test_reg_entry_point_handler(mock_context: MagicMock, mock_update: Update, mock_new_user: MagicMock, ):
    # "return_value" to attach (make a child) future mock to mock_context
    with patch_object(
            CLS_TO_TEST,
            'NewUserForm',
            
            return_value=mock_new_user,
    ) as mock_new_user_cls:  # Note by inject_new_user_form fixture new_user form already exists at this moment
        result = await CLS_TO_TEST.entry_point_handler(_=mock_update, context=mock_context, )
    # Checks
    mock_new_user_cls.acow(user=mock_context.user)
    assert mock_context.user_data.forms.new_user == mock_new_user_cls.return_value
    mock_context.view.reg.ask_user_name.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 1


async def test_name_handler_incorrect(mock_context: MagicMock, mock_update: Update, ):
    mock_update.effective_message.text = 'foo'
    mock_context.user_data.forms.new_user.handle_name.side_effect = EXCEPTION
    # Execution
    result = await CLS_TO_TEST.name_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_name.acow(text='foo')
    mock_context.view.reg.warn.incorrect_name.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[generator.gen_fullname()]), )
async def test_name_handler(mock_context: MagicMock, mock_update: Update, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.name_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_name.acow(text=text)
    mock_context.view.reg.ask_user_goal.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 2


async def test_goal_handler_incorrect(mock_context: MagicMock, mock_update: Update, ):
    mock_update.effective_message.text = 'foo'
    mock_context.user_data.forms.new_user.handle_goal.side_effect = EXCEPTION
    # Execution
    result = await CLS_TO_TEST.goal_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_goal.acow(text='foo')
    mock_context.view.reg.warn.incorrect_goal.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=CLS_TO_TEST.Texts.REG_GOALS))
async def test_goal_handler(mock_context: MagicMock, mock_update: Update, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.goal_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_goal.acow(text=text)
    mock_context.view.reg.ask_user_gender.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result == 3


async def test_gender_handler_incorrect(mock_context: MagicMock, mock_update: Update, ):
    mock_update.effective_message.text = 'foo'
    mock_context.user_data.forms.new_user.handle_gender.side_effect = EXCEPTION
    # Execution
    result = await CLS_TO_TEST.gender_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_gender.acow(text='foo')
    mock_context.view.reg.warn.incorrect_gender.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=CLS_TO_TEST.Texts.REG_GENDERS))
async def test_gender_handler(mock_context: MagicMock, mock_update: Update, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.gender_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_gender.acow(text=text)
    mock_context.view.reg.ask_user_age.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 4


async def test_age_handler_incorrect(mock_context: MagicMock, mock_update: Update, ):
    mock_update.effective_message.text = 'foo'
    mock_context.user_data.forms.new_user.handle_age.side_effect = EXCEPTION
    # Execution
    result = await CLS_TO_TEST.age_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_age.acow(text='foo')
    mock_context.view.reg.warn.incorrect_age.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
async def test_age_handler(mock_context: MagicMock, mock_update: Update, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.age_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_age.acow(text=text)
    mock_context.view.reg.ask_user_location.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 5


class TestLocationHandler:
    """location_handler"""

    @staticmethod
    async def test_geo_incorrect(mock_context: MagicMock, mock_update: Update, ):
        mock_context.user_data.forms.new_user.handle_location_geo.side_effect = CLS_TO_TEST.BadLocation
        # Execution
        result = await CLS_TO_TEST.location_handler_geo(update=mock_update, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.acow(
            location=mock_update.effective_message.location,
        )
        mock_context.view.reg.warn.incorrect_location.acow()
        assert len(mock_context.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None

    @staticmethod
    async def test_geo_location_service_error(mock_context: MagicMock, mock_update: Update, ):
        mock_context.user_data.forms.new_user.handle_location_geo.side_effect = CLS_TO_TEST.LocationServiceError
        # Execution
        result = await CLS_TO_TEST.location_handler_geo(update=mock_update, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.acow(
            location=mock_update.effective_message.location,
        )
        mock_context.view.location_service_error.acow()
        assert len(mock_context.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None

    @staticmethod
    async def test_geo_success(mock_context: MagicMock, mock_update: Update, ):
        result = await CLS_TO_TEST.location_handler_geo(update=mock_update, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.acow(
            location=mock_update.effective_message.location,
        )
        mock_context.view.reg.ask_user_photos.acow()
        assert len(mock_context.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result == 6

    @staticmethod
    async def test_text_incorrect(mock_context: MagicMock, mock_update: Update, ):
        mock_context.user_data.forms.new_user.handle_location_text.side_effect = EXCEPTION
        # Execution
        result = await CLS_TO_TEST.location_handler_text(update=mock_update, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_text.acow(
            text=mock_update.effective_message.text,
        )
        mock_context.view.reg.warn.incorrect_location.acow()
        assert len(mock_context.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
async def test_text_success(mock_context: MagicMock, mock_update: Update, text: str, ):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.location_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_location_text.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.reg.ask_user_photos.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 6


async def test_photos_handler_tg_photo_success(
        mock_update: Update,
        mock_context: MagicMock,

):
    return_value = CLS_TO_TEST.Texts.PHOTO_ADDED_SUCCESS
    mock_context.user_data.forms.new_user.handle_photo_tg_object.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_tg_photo(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.acow(
        photo=mock_update.effective_message.photo,
        media_group_id=mock_update.effective_message.media_group_id,
    )
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.view.reg.say_photo_added_success.acow(keyboard=keyboard, )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


async def test_photos_handler_tg_photo_too_many_photos(
        mock_update: Update,
        mock_context: MagicMock,

):
    return_value = CLS_TO_TEST.Texts.TOO_MANY_PHOTOS
    mock_context.user_data.forms.new_user.handle_photo_tg_object.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_tg_photo(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.acow(
        photo=mock_update.effective_message.photo,
        media_group_id=mock_update.effective_message.media_group_id,
    )
    mock_context.view.reg.warn.too_many_photos.acow(
        keyboard=mock_context.user_data.forms.new_user.current_keyboard,
        used_photos=len(mock_context.user_data.forms.new_user.photos),
    )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


@pytest_mark.parametrize(argnames='media_group_id', argvalues=['1', '2'])
async def test_photos_handler_tg_album_photo(
        mock_update: Update,
        mock_context: MagicMock,
        media_group_id: str,

):
    mock_update.effective_message.media_group_id = media_group_id
    # Execution
    result = await CLS_TO_TEST.photos_handler_tg_photo(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.acow(
        photo=mock_update.effective_message.photo,
        media_group_id=mock_update.effective_message.media_group_id,
    )
    assert len(mock_context.view.mock_calls) == 0
    assert len(mock_context.mock_calls) == 0
    assert result is None  # Same state because still waiting for photos


async def test_photos_handler_text_account_photos(
        mock_update: Update,
        mock_context: MagicMock,

):
    """app.constants.FINISH Should be in another test because will lead to next stage"""
    return_value = CLS_TO_TEST.Texts.PHOTOS_ADDED_SUCCESS
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(text=ANY, )
    mock_context.view.reg.say_photo_added_success.acow(
        keyboard=mock_context.user_data.forms.new_user.current_keyboard,
    )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


async def test_photos_handler_text_incorrect(
        mock_update: Update,
        mock_context: MagicMock,

):
    """app.constants.FINISH Should be in another test because will lead to next stage"""
    return_value = CLS_TO_TEST.Texts.INCORRECT_FINISH
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.warn.incorrect_finish.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


async def test_photos_handler_text_no_photos_to_remove(
        mock_update: Update,
        mock_context: MagicMock,

):
    return_value = CLS_TO_TEST.Texts.NO_PHOTOS_TO_REMOVE
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(text=ANY)
    mock_context.view.reg.warn.no_profile_photos.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


async def test_photos_handler_text_photos_removed_success(
        mock_update: Update,
        mock_context: MagicMock,

):
    return_value = CLS_TO_TEST.Texts.PHOTOS_REMOVED_SUCCESS
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = return_value
    # Execution
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(text=ANY)
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.view.reg.say_photos_removed_success.acow(keyboard=keyboard)
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


async def test_photos_handler_text_too_many_photos(
        mock_update: Update,
        mock_context: MagicMock,
):
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = CLS_TO_TEST.Texts.TOO_MANY_PHOTOS
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(text=ANY)
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.view.reg.warn.too_many_photos.acow(keyboard=keyboard, used_photos=0, )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


async def test_photos_handler_finish(mock_update: Update, mock_context: MagicMock, ):
    mock_context.user_data.forms.new_user.handle_photo_text.return_value = CLS_TO_TEST.Texts.FINISH_KEYWORD
    # Execution
    result = await CLS_TO_TEST.photos_handler_text(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.acow(text=ANY)
    mock_context.view.reg.ask_user_comment.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 7


async def test_comment_handler_incorrect(
        mock_update: Update,
        mock_context: MagicMock,

):
    mock_update.effective_message.text = 'foo'  # To apply len method on string, was None
    mock_context.user_data.forms.new_user.handle_comment.side_effect = EXCEPTION
    # Execution
    result = await CLS_TO_TEST.comment_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_comment.acow(
        text=mock_update.effective_message.text
    )
    mock_context.view.reg.warn.comment_too_long.acow(
        comment_len=len(mock_update.effective_message.text),
    )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


async def test_comment_handler(
        mock_update: Update,
        mock_context: MagicMock,
):
    mock_update.effective_message.text = generator.gen_comment()
    # Execution
    result = await CLS_TO_TEST.comment_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_comment.acow(
        text=mock_update.effective_message.text,
    )
    mock_context.view.reg.show_new_user.acow(
        new_user=mock_context.user_data.forms.new_user,
    )
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 8


async def test_confirm_handler_incorrect(mock_update: Update, mock_context: MagicMock, ):
    mock_update.effective_message.text = 'foo'
    # Execution
    result = await CLS_TO_TEST.confirm_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.view.reg.warn.incorrect_end_reg.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


@pytest_mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[CLS_TO_TEST.Texts.FINISH_KEYWORD], ))
async def test_confirm_handler(
        mock_update: Update,
        mock_context: MagicMock,
        text: str,
):
    mock_update.effective_message.text = text
    # Execution
    result = await CLS_TO_TEST.confirm_handler(update=mock_update, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.create.acow()
    mock_context.view.reg.say_success_reg.acow()
    assert len(mock_context.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == -1
