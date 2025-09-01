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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, Protocol, Type, TypedDict, Sequence
from dataclasses import dataclass
from string import punctuation as string_punctuation

from telegram.error import TelegramError
from telegram.constants import ParseMode, MediaGroupLimit
from telegram.helpers import mention_html
from telegram import (
    ReplyKeyboardMarkup as tg_RKM,
    ReplyKeyboardRemove,
    InputMediaPhoto,
    InlineKeyboardButton as tg_IKB,
    InlineKeyboardMarkup as tg_IKM,
    KeyboardButton,
    KeyboardButtonRequestUsers,
)
from telegram.ext import ExtBot

from rubik_core.shared.structures import Goal, Gender

from app.config import DEFAULT_PHOTO_PATH
from .constants import HIDE_S
from . import texts
from ..post.constants import PostsChannels

from app.tg.ptb import bot
from app.tg.ptb.custom import extract_shared_user_name

if TYPE_CHECKING:
    from telegram import (
        CallbackQuery,
        Message,
        MessageId,
        KeyboardButton as tg_KB,
        SharedUser,
    )
    from ..user.model import IUser


class SharedInit:

    bot: ExtBot = bot

    def __init__(self, user: IUser, ):
        self.id = user.id
        self.user = user


class Shared(SharedInit, ):
    def __init__(self, user: IUser, ):
        super().__init__(user=user, )
        self.warn = self.Warn(user=user, )

    class Warn(SharedInit, ):

        async def incorrect_finish(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=texts.Warn.INCORRECT_FINISH, )

        async def text_too_long(self, max_symbols: int, used_symbols: int, ):
            return await self.bot.send_message(
                chat_id=self.id,
                text=texts.Warn.TEXT_TOO_LONG.format(MAX_TEXT_LEN=max_symbols, USED_TEXT_LEN=used_symbols, ),
                reply_markup=Keyboards.cancel
            )

        async def unskippable_step(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=texts.Warn.UNSKIPPABLE_STEP, )

        async def incorrect_send(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=texts.Warn.INCORRECT_SEND, )

        async def incorrect_continue(self, keyword: str = texts.Words.CONTINUE, ) -> Message:
            return await self.bot.send_message(
                chat_id=self.id,
                text=texts.Warn.INCORRECT_CONTINUE.format(CONTINUE=keyword, ),
            )

        async def incorrect_user(self, ) -> Message:
            return await self.bot.send_message(chat_id=self.id, text=texts.Warn.INCORRECT_USER, )

        async def nan_help_msg(self, ) -> Message:  # Not in use
            return await self.bot.send_message(
                text=f'{texts.Warn.MISUNDERSTAND}\n{texts.ENTER_THE_NUMBER}',
                chat_id=self.id
            )

    async def say_ok(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=texts.Words.OK, )

    async def notify_ready_keyword(self, keyword: str = texts.Words.READY, ) -> Message:
        if keyword == texts.Words.READY:
            keyboard = Keyboards.ready_cancel
        else:
            keyboard = Keyboards.cancel_factory(buttons=[keyword, ], )
        return await self.bot.send_message(
            chat_id=self.id,
            text=texts.FOR_READY.format(READY=keyword, ),
            reply_markup=keyboard,
        )

    async def cancel(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=texts.Words.CANCELED,
            reply_markup=Keyboards.remove(),
        )

    async def location_service_error(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=texts.Warn.ERROR_LOCATION_SERVICE, )

    async def user_not_found(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            # Note: "format" here because:
            # 1. Technically, bot.username may be changed during execution
            # 2. Bot not initialized during PTB texts creation stage, so bot.username inaccessible without tricks
            # BOT_USERNAME - link to share with user to him to the bot
            text=texts.Warn.ALAS_USER_NOT_FOUND.format(BOT_USERNAME=f'@{self.bot.username}'),
        )

    @staticmethod
    async def unclickable_button(tooltip: CallbackQuery, ) -> bool:
        return await tooltip.answer(text=texts.Warn.UNCLICKABLE_BUTTON, )

    @staticmethod
    async def unknown_button(tooltip: CallbackQuery, ) -> bool:
        return await tooltip.answer(text=texts.Warn.UNKNOWN_BUTTON, )

    async def easter_egg(self, ) -> None:
        sent_message = await self.bot.send_message(
            chat_id=self.id,
            text=texts.EASTER_EGG,
            reply_markup=Keyboards.remove(),
        )
        await self.bot.delete_message(chat_id=sent_message.chat_id, message_id=sent_message.message_id, )

    async def say_user_got_share_proposal(self, shared_recipient: SharedUser, ):
        return await self.bot.send_message(
            chat_id=self.id,
            text=texts.USER_GOT_SHARE_PROPOSAL.format(
                USERNAME=mention_html(
                    user_id=shared_recipient.user_id,
                    name=extract_shared_user_name(shared_user=shared_recipient, ),
                ), ),
            parse_mode=ParseMode.HTML,  # HTML is a bit safer cuz not requiring escaping
        )

    async def say_user_got_request_proposal(self, shared_recipient: SharedUser, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=texts.USER_GOT_REQUEST_PROPOSAL.format(
                USERNAME=mention_html(
                    user_id=shared_recipient.user_id,
                    name=extract_shared_user_name(shared_user=shared_recipient, ),
                ), ),
            parse_mode=ParseMode.HTML,  # HTML is a bit safer cuz not requiring escaping
        )

    async def user_declined_share_proposal(self, id: int, decliner_username: str, ) -> Message:
        return await self.bot.send_message(
            chat_id=id,
            text=texts.USER_DECLINED_SHARE_PROPOSAL.format(DECLINER_USERNAME=decliner_username),
        )

    """
    async def user_accepted_share_proposal(self, ) -> Message:
        No need base accept cuz message is differ for all (unlike for decline)
    """

    async def user_declined_request_proposal(self, id: int, decliner_username: str, ) -> Message:
        return await self.bot.send_message(
            chat_id=id,
            text=texts.USER_DECLINED_REQUEST_PROPOSAL.format(DECLINER_USERNAME=decliner_username),
        )

    @classmethod
    async def remove_sharing_message(cls, message: Message, ) -> bool:
        """
        Should be classmethod to ignore automatically passed self/cls object
        when assigned directly to view class without wrapper function
        """
        return await message.delete()

    async def internal_error(
            self,
            tooltip: CallbackQuery = None,
            force_alert: bool = False,
    ) -> (Message | bool):
        if tooltip:
            return await tooltip.answer(text=texts.INTERNAL_ERROR, show_alert=force_alert, )
        else:
            return await self.bot.send_message(
                chat_id=self.id,
                text=texts.INTERNAL_ERROR,
                reply_markup=ReplyKeyboardRemove(),
            )

    async def check_message_existence(self, chat_id: int, message_id: int, ) -> bool:
        """
        Telegram bot api has no direct way to check is message exists, so it's a tricky way
        https://github.com/tdlib/telegram-bot-api/issues/62
        """
        try:
            sent_message_obj = await self.bot.copy_message(
                chat_id=PostsChannels.STORE.value,
                from_chat_id=chat_id,
                message_id=message_id,
            )
            await self.bot.delete_message(chat_id=PostsChannels.STORE.value, message_id=sent_message_obj.message_id, )
            return True
        except TelegramError:
            return False

    async def add_close_btn(
            self,
            message_ids_to_close: Sequence[int | MessageId | Message],
            keyboard: tg_IKM,
    ) -> None:
        """The last message will get the btn"""
        if isinstance(message_ids_to_close[-1], int):
            message_id_with_btn = message_ids_to_close[-1]
        else:  # If Message or MessageId
            message_id_with_btn = message_ids_to_close[-1].message_id
        await self.bot.edit_message_reply_markup(
            chat_id=self.id,
            message_id=message_id_with_btn,
            reply_markup=Keyboards.add_btn(
                keyboard=keyboard,
                btn=Keyboards.get_close_btn(message_ids_to_close=message_ids_to_close, )
            )
        )


class ProfileText(TypedDict):
    name: str
    goal: str
    gender: str
    age: int
    location: str
    comment: str


class ProfileDataDB(ProfileText):
    photos: list[str]


class ProfileProtocol(Protocol, ):
    fullname: str
    goal: Goal
    gender: Gender
    age: int
    city: str
    country: str
    comment: str
    photos: list[str]


@dataclass(slots=True, )
class Payload:
    text: str
    photos: list[str]


class IProfileBase(ABC, ):

    Goal: Goal
    Gender: Gender
    DEFAULT_MEDIA_PHOTO: InputMediaPhoto

    UserModel: Type[UserModel]
    Payload: Type[Payload] = Payload
    TranslationsMap: dict

    @abstractmethod
    def translate_goal(self) -> str:
        ...

    @abstractmethod
    def translate_gender(self) -> str:
        ...

    @abstractmethod
    def get_profile_text(self) -> str:
        ...

    @abstractmethod
    def translate_text(self, ):
        ...

    @abstractmethod
    def get_payload(self, ):
        ...

    @abstractmethod
    def prepare_photos_to_send(self, caption: str, ) -> list[InputMediaPhoto]:
        ...

    @abstractmethod
    async def send(self, show_to_id: int = None, ) -> None:
        ...


class ProfileBase(IProfileBase, ):

    Goal = Goal
    Gender = Gender
    DEFAULT_MEDIA_PHOTO = InputMediaPhoto(media=DEFAULT_PHOTO_PATH.read_bytes(), parse_mode=ParseMode.HTML, )

    Payload: Type[Payload] = Payload
    TranslationsMap: dict

    def __init__(self, bot: ExtBot, data_source: ProfileProtocol, id: int, ):
        self.bot = bot
        self.data = data_source
        self.id = id

    def translate_goal(self) -> str:
        return self.TranslationsMap[self.Goal].get(self.data.goal, texts.Words.UNKNOWN, )

    def translate_gender(self) -> str:
        return self.TranslationsMap[self.Gender].get(self.data.gender, texts.Words.UNKNOWN, )

    def translate_location(self) -> str | None:
        return ', '.join(x for x in [self.data.country, self.data.city] if x is not None) or None

    def translate_text(self, ) -> ProfileText:
        """
        Convert user attributes to human-readable views
        Don't forget to use parse_mode="HTML" if you are using links
        """
        text = {
            texts.Profile.NAME: f"<a href='tg://user?id={self.id}'>{self.data.fullname}</a>",
            texts.Profile.GOAL: self.translate_goal(),
            texts.Profile.GENDER: self.translate_gender(),
            texts.Profile.AGE: self.data.age,
            texts.Profile.LOCATION: self.translate_location(),
            texts.Profile.ABOUT: self.data.comment,
        }
        return {k: v for k, v in text.items() if v is not None}

    def get_profile_text(self) -> str:
        text = '\n'.join(f'<b>{k}</b> - <code><i>{v}</i></code>.' for k, v in self.translate_text().items())
        text = text if text[-1] in string_punctuation else f'{text}'
        return text

    def get_payload(self, ) -> Payload:
        """Profile text and photo"""
        profile_text = self.get_profile_text()
        return self.Payload(text=profile_text, photos=self.data.photos, )

    def prepare_photos_to_send(self, caption: str, ) -> list[InputMediaPhoto]:
        photos_to_send = []
        for photo in self.data.photos[:MediaGroupLimit.MAX_MEDIA_LENGTH]:  # TG allows max ~10 photos per message
            # Only first photo need a caption ?
            photos_to_send.append(InputMediaPhoto(media=photo, parse_mode=ParseMode.HTML, caption=caption, ))
        photos_to_send = photos_to_send or [self.DEFAULT_MEDIA_PHOTO]
        return photos_to_send

    async def send(self, show_to_id: int = None, ) -> None:
        show_to_id = show_to_id or self.id
        profile_data = self.get_payload()
        photos_to_send = self.prepare_photos_to_send(caption=profile_data.text, )
        await self.bot.send_media_group(chat_id=show_to_id, media=photos_to_send, parse_mode=ParseMode.HTML, )
        if len(profile_data.photos) > 1:  # Tg hides text if photos > 1, so send text explicit in this case
            await self.bot.send_message(chat_id=show_to_id, text=profile_data.text, parse_mode=ParseMode.HTML, )


class Keyboards:

    HIDE_S = HIDE_S

    cancel = tg_RKM(
        keyboard=[[texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    continue_cancel = tg_RKM(
        keyboard=[[texts.Words.CONTINUE], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    ready_cancel = tg_RKM(
        keyboard=[[texts.Words.READY], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    send_cancel = tg_RKM(
        keyboard=[[texts.Words.SEND], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    skip_cancel = tg_RKM(
        keyboard=[[texts.Words.SKIP], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    finish_cancel = tg_RKM(
        keyboard=[[texts.Words.FINISH], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    remove = ReplyKeyboardRemove

    go = tg_RKM(
        keyboard=[[texts.Words.GO], [texts.Words.CANCEL]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    @staticmethod
    def cancel_factory(buttons: Iterable[tg_KB | str], *args, **kwargs, ) -> tg_RKM:
        """May be improved by making keyboard (default cancel) as param"""
        # TODO use add_btn
        kwargs.setdefault('resize_keyboard', True, )
        kwargs.setdefault('one_time_keyboard', True, )
        return tg_RKM(keyboard=(buttons, (texts.Words.CANCEL,),), *args, **kwargs, )

    @classmethod
    def get_close_btn(cls, message_ids_to_close: Sequence[int | MessageId | Message], ) -> tg_IKB | None:
        ids = []
        for message_id in message_ids_to_close:
            if isinstance(message_id, int):
                ids.append(str(message_id))
            else:
                ids.append(str(message_id.message_id))
        return tg_IKB(text=texts.Words.HIDE, callback_data=f'{cls.HIDE_S} {" ".join(ids)}')

    @staticmethod
    def get_show_profile_btn(user_id: int, ) -> tg_IKB:
        return tg_IKB(text=texts.Words.SHOW_PROFILE, callback_data=f'{texts.Words.SHOW_PROFILE} {user_id}', )

    @classmethod
    def add_btn(cls, keyboard: tg_IKM, btn: tg_IKB, ) -> tg_IKM:
        """Returns the new keyboard object"""
        return tg_IKM(inline_keyboard=(*keyboard.inline_keyboard, (btn,),), )

    @classmethod
    def check_is_close_btn(cls, btn: tg_IKB, ) -> bool:
        """Can't compare with entire button cuz it always has different cbk (messages to cose)"""
        return btn.callback_data.startswith(cls.HIDE_S)

    @classmethod
    def request_user(cls, request_btn_params: dict | None = None, ) -> tg_RKM:
        """Returns new keyboard obj."""
        new_keyboard = tg_RKM(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=((KeyboardButton(
                text='Выбрать пользователя',
                # Note: May be selected multiple chats
                request_users=KeyboardButtonRequestUsers(request_id=1, **(request_btn_params or {}), ),
            ),),),
        )
        return new_keyboard
