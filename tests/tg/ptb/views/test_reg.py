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

from app.tg.ptb.entities.user.view import Reg as View, Keyboards
from app.tg.ptb.entities.user.model import User
from app.tg.ptb.entities.user.texts import Reg as Texts

from app.tg.ptb.entities.texts import PUBLIC_COMMANDS

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestWarn:
    @staticmethod
    async def test_incorrect_name(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_name(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_NAME,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_goal(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_goal(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_GOAL,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_gender(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_gender(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_GENDER,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_age(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_age(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_AGE,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_location(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_location(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_LOCATION,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_no_profile_photos(mock_view_f: MagicMock, ):
        result = await View.Warn.no_profile_photos(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.NO_PROFILE_PHOTOS,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_too_many_photos(mock_view_f: MagicMock, ):
        result = await View.Warn.too_many_photos(self=mock_view_f.reg.warn, keyboard=typing_Any, used_photos=3, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.TOO_MANY_PHOTOS.format(USED_PHOTOS=3, ),
            reply_markup=typing_Any
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_incorrect_photo(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_photo(self=mock_view_f.reg.warn, keyboard=typing_Any)
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.INCORRECT_FINISH,
            reply_markup=typing_Any
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    async def test_comment_too_long(mock_view_f: MagicMock, ):
        result = await View.Warn.comment_too_long(self=mock_view_f.reg.warn, comment_len=100, )
        mock_view_f.reg.warn.SharedView.Warn.text_too_long.acow(
            max_symbols=User.MAX_COMMENT_LEN,
            used_symbols=100,
        )
        assert result == mock_view_f.reg.warn.SharedView.Warn.text_too_long.return_value

    @staticmethod
    async def test_incorrect_end_reg(mock_view_f: MagicMock, ):
        result = await View.Warn.incorrect_end_reg(self=mock_view_f.reg.warn, )
        mock_view_f.reg.warn.bot.send_message.acow(
            chat_id=mock_view_f.reg.warn.id,
            text=Texts.END_REG_HELP,
        )
        assert result == mock_view_f.reg.warn.bot.send_message.return_value


async def test_say_reg_hello(mock_view_f: MagicMock):
    result = await View.say_reg_hello(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_0,
        reply_markup=Keyboards.go,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_name(mock_view_f: MagicMock):
    result = await View.ask_user_name(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_1,
        reply_markup=Keyboards.ask_user_name(mock_view_f.user.ptb.name, ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_goal(mock_view_f: MagicMock):
    result = await View.ask_user_goal(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_2,
        reply_markup=Keyboards.ask_user_goal,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_gender(mock_view_f: MagicMock):
    result = await View.ask_user_gender(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_3,
        reply_markup=Keyboards.ask_user_gender,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_age(mock_view_f: MagicMock, ):
    result = await View.ask_user_age(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_4,
        reply_markup=Keyboards.ask_user_age,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_location(mock_view_f: MagicMock, ):
    result = await View.ask_user_location(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_5,
        reply_markup=Keyboards.ask_user_location,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_photos(mock_view_f: MagicMock, ):
    result = await View.ask_user_photos(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_6,
        reply_markup=Keyboards.original_photo_keyboard,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_photo_added_success(mock_view_f: MagicMock, ):
    keyboard = Keyboards.original_photo_keyboard
    result = await View.say_photo_added_success(self=mock_view_f, keyboard=keyboard, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.PHOTOS_ADDED_SUCCESS,
        reply_markup=keyboard,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_photos_removed_success(mock_view_f: MagicMock, ):
    result = await View.say_photos_removed_success(self=mock_view_f, keyboard=typing_Any, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.PHOTOS_REMOVED_SUCCESS,
        reply_markup=typing_Any,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_user_comment(mock_view_f: MagicMock, ):
    result = await View.ask_user_comment(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.STEP_7,
        reply_markup=Keyboards.ask_user_comment
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_new_user_profile(mock_view_f: MagicMock, mock_new_user: MagicMock, ):
    await View.show_new_user(self=mock_view_f.reg, new_user=mock_new_user, )
    mock_view_f.reg.bot.send_message.acow(
        chat_id=mock_view_f.reg.id,
        text=Texts.HERE_PROFILE_PREVIEW,
        reply_markup=Keyboards.ask_user_confirm,
    )
    mock_view_f.reg.Profile.return_value.send.acow(show_to_id=mock_view_f.reg.id, )


async def test_say_success_reg(mock_view_f: MagicMock, ):
    result = await View.say_success_reg(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{Texts.SUCCESS_REG}\n\n{Texts.MORE_ACTIONS}\n{PUBLIC_COMMANDS}',
        reply_markup=Keyboards.say_success_reg()
    )
    assert result == mock_view_f.bot.send_message.return_value
