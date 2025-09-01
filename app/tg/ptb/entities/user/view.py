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
from typing import TYPE_CHECKING, Callable, Any as typing_Any

from telegram import (
    ReplyKeyboardMarkup as tg_RKM,
    KeyboardButton as tg_KB,
)

from .model import User
from ..shared.view import SharedInit, Shared, Keyboards as SharedKeyboards, ProfileBase, IProfileBase
from .texts import Reg as Texts
from ..texts import PUBLIC_COMMANDS

if TYPE_CHECKING:
    from telegram import Message, ReplyKeyboardMarkup as tg_RKM
    from .model import IUser
    from .forms import INewUser


class Profile(ProfileBase, IProfileBase, ):

    TranslationsMap = {
        User.Goal: {
            User.Goal.CHAT: Texts.Profile.I_WANNA_CHAT,
            User.Goal.DATE: Texts.Profile.I_WANNA_DATE,
            User.Goal.BOTH: Texts.Profile.I_WANNA_CHAT_AND_DATE,
        },
        User.Gender: {
            User.Gender.MALE: Texts.Profile.I_MALE,
            User.Gender.FEMALE: Texts.Profile.I_FEMALE,
        },
    }


class Reg(SharedInit, ):
    Profile = Profile

    class Warn(SharedInit, ):
        SharedView = Shared

        async def incorrect_name(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.INCORRECT_NAME, )

        async def incorrect_goal(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.INCORRECT_GOAL, )

        async def incorrect_gender(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.INCORRECT_GENDER, )

        async def incorrect_age(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.INCORRECT_AGE, )

        async def incorrect_location(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.INCORRECT_LOCATION, )

        async def no_profile_photos(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.NO_PROFILE_PHOTOS, )

        async def too_many_photos(self, keyboard: tg_RKM, used_photos: int, ):
            return await self.bot.send_message(
                chat_id=self.id,
                text=Texts.TOO_MANY_PHOTOS.format(
                    USED_PHOTOS=used_photos,
                    MAX_PHOTOS=User.MAX_PHOTOS_COUNT,
                ),
                reply_markup=keyboard,
            )

        async def incorrect_photo(self, keyboard: tg_RKM, ):
            return await self.bot.send_message(
                chat_id=self.id,
                text=Texts.INCORRECT_FINISH,
                reply_markup=keyboard,
            )

        async def comment_too_long(self, comment_len: int, ):
            return await self.SharedView.Warn.text_too_long(
                max_symbols=User.MAX_COMMENT_LEN,
                used_symbols=comment_len,
            )

        async def incorrect_end_reg(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=Texts.END_REG_HELP, )

    def __init__(self, user: IUser, ):
        super().__init__(user=user, )
        self.warn = self.Warn(user=user, )

    async def say_reg_hello(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_0,
            reply_markup=Keyboards.go,
        )

    async def ask_user_name(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_1,
            reply_markup=Keyboards.ask_user_name(name=self.user.ptb.name, ),
        )

    async def ask_user_goal(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_2,
            reply_markup=Keyboards.ask_user_goal,
        )

    async def ask_user_gender(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_3,
            reply_markup=Keyboards.ask_user_gender,
        )

    async def ask_user_age(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_4,
            reply_markup=Keyboards.ask_user_age,
        )

    async def ask_user_location(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_5,
            reply_markup=Keyboards.ask_user_location,
        )

    async def ask_user_photos(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_6,
            reply_markup=Keyboards.original_photo_keyboard,
        )

    async def say_photo_added_success(self, keyboard: tg_RKM, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.PHOTOS_ADDED_SUCCESS,
            reply_markup=keyboard,
        )

    async def say_photos_removed_success(self, keyboard: tg_RKM, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.PHOTOS_REMOVED_SUCCESS,
            reply_markup=keyboard,
        )

    async def ask_user_comment(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.STEP_7,
            reply_markup=Keyboards.ask_user_comment, )

    async def say_success_reg(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=f'{Texts.SUCCESS_REG}\n\n{Texts.MORE_ACTIONS}\n{PUBLIC_COMMANDS}',
            reply_markup=Keyboards.say_success_reg(),  # Call cuz it remove indeed
        )

    async def show_new_user(self, new_user: INewUser, ) -> None:
        """Different keyboard with match profile"""
        profile = self.Profile(bot=self.bot, data_source=new_user, id=self.id, )
        await self.bot.send_message(
            chat_id=self.id,
            text=Texts.HERE_PROFILE_PREVIEW,
            reply_markup=Keyboards.ask_user_confirm,
        )
        await profile.send(show_to_id=self.id, )


class Keyboards:
    go = SharedKeyboards.go
    ask_user_name: Callable[[typing_Any], tg_RKM] = lambda name: tg_RKM(
        keyboard=[[f'{Texts.Buttons.USE_ACCOUNT_NAME} ("{name}")'], [Texts.CANCEL_KEYWORD]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_user_goal = tg_RKM(
        keyboard=[
            [Texts.Buttons.I_WANNA_CHAT, Texts.Buttons.I_WANNA_DATE],
            [Texts.Buttons.I_WANNA_CHAT_AND_DATE],
            [Texts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_user_gender = tg_RKM(
        keyboard=[
            [Texts.Buttons.I_FEMALE, Texts.Buttons.I_MALE],
            [Texts.CANCEL_KEYWORD]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_user_age = SharedKeyboards.cancel

    ask_user_location = tg_RKM(
        keyboard=[
            [tg_KB(text=Texts.Buttons.SEND_LOCATION, request_location=True)],
            [Texts.SKIP_KEYWORD],
            [Texts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ask_user_comment = SharedKeyboards.skip_cancel

    ask_user_confirm = tg_RKM(
        keyboard=[
            [Texts.FINISH_KEYWORD],
            [Texts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    original_photo_keyboard = tg_RKM(
        keyboard=[
            [Texts.FINISH_KEYWORD],
            [Texts.Buttons.USE_ACCOUNT_PHOTOS],
            [Texts.CANCEL_KEYWORD],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    remove_photos_keyboard = tg_RKM(
        keyboard=[
            [Texts.FINISH_KEYWORD],
            [Texts.Buttons.REMOVE_PHOTOS],
            [Texts.CANCEL_KEYWORD]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    say_success_reg = SharedKeyboards.remove
