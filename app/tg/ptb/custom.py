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
from typing import TYPE_CHECKING, Sequence, Iterable, Any
from asyncio import wait_for as asyncio_wait_for, TimeoutError as asyncio_TimeoutError

from telegram.constants import ChatType
from telegram.error import TelegramError
from telegram import InlineKeyboardButton as tg_IKB, SharedUser
from telegram.ext import ConversationHandler

from rubik_core.shared.utils import get_num_from_text as rubik_core_get_num_from_text

from app.tg.telethon import username_to_user as username_to_telethon_user

if TYPE_CHECKING:
    from re import Pattern, Match
    from telegram import Message, InlineKeyboardMarkup as tg_IKM, ChatFullInfo
    from telegram.ext import Application, ExtBot


def end_conversation() -> int:  # Move to shared_handlers
    return ConversationHandler.END


async def username_to_id(app: Application, username: str, raise_: bool = True, timeout: float = 5, ) -> int:
    try:
        task = app.create_task(coroutine=username_to_telethon_user(username=username, raise_=raise_, ), )
        result = await asyncio_wait_for(fut=task, timeout=timeout, )
    except asyncio_TimeoutError:
        return 0  # TODO behavior
    return result.id


async def get_chat(chat_id: int, bot: ExtBot, read_timeout: int | None = None, ) -> ChatFullInfo:
    chat_full_info = await bot.get_chat(
        chat_id=chat_id,
        read_timeout=read_timeout,
    )
    return chat_full_info


async def accept_user(app: Application, message: Message, check: bool = False, ) -> int | None:
    """
    Request a recipient (user) to send a message from a sender (user) to this user
    """
    if message.users_shared:  # Note: May be select multiple
        chat_id = message.users_shared.users[0].user_id
    elif hasattr(message.contact, 'user_id', ):  # user_id of message.contact may be None
        chat_id = message.contact.user_id
    elif message.text:
        if message.text.startswith('@'):
            chat_id = await username_to_id(app=app, username=message.text, raise_=False, )
        else:
            chat_id = rubik_core_get_num_from_text(text=message.text, )
            if message.chat.type == ChatType.CHANNEL:
                chat_id = int(f'-100{chat_id}')
    else:
        return None
    if check:
        # If not exists - TelegramError (or BadRequest in the newest versions) will be raised
        await message.get_bot().get_chat(chat_id=chat_id, )
    return chat_id


async def request_user(app: Application, message: Message, ) -> SharedUser | None:
    """Advanced version of accept_user"""
    if message.users_shared:  # Note: May be select multiple
        return message.users_shared.users[0]
    input_chat_id = await accept_user(app=app, message=message, check=False, )
    if input_chat_id:
        try:
            chat_info = await message.get_bot().get_chat(chat_id=input_chat_id, )
        except TelegramError:  # pragma: no cover
            return None
        return SharedUser(
            user_id=chat_info.id,
            username=chat_info.username,
            first_name=chat_info.first_name,
            last_name=chat_info.last_name,
        )


def extract_shared_user_name(shared_user: SharedUser, ) -> str:
    if shared_user.username:
        return f'@{shared_user.username}'
    elif shared_user.first_name and shared_user.last_name:
        return f'{shared_user.first_name} {shared_user.last_name}'
    else:
        return shared_user.first_name or shared_user.last_name or str(shared_user.user_id)


class CustomInlineKeyboardMarkup:

    @classmethod
    def to_list(cls, inline_keyboard: tuple[tuple[tg_IKB, ...], ...]) -> list[list[tg_IKB]]:
        """Not in use, just in case for future"""
        new_keyboard = [list(row) for row in inline_keyboard]
        return new_keyboard

    @classmethod
    def find_btn_by_cbk(cls, inline_keyboard: Sequence[Sequence[tg_IKB]], cbk: str, ) -> tuple[tg_IKB, int, int]:
        for row_index, row in enumerate(inline_keyboard):
            for column_index, column in enumerate(row):
                # in instead of == to keep ability to match by prefix and some cbk key if need it
                if cbk in inline_keyboard[row_index][column_index].callback_data:
                    return inline_keyboard[row_index][column_index], row_index, column_index

    @classmethod
    def get_keyboard_buttons(cls, inline_keyboard: Iterable[Iterable[tg_IKB]], ) -> list[tg_IKB]:
        """Flatten"""
        result = []
        for row in inline_keyboard:
            for btn in row:
                result.append(btn)
        return result

    @classmethod
    def split(
            cls,  # Rename params to the same style (btns | buttons | num_in_row) ?
            btns_in_row: int,
            inline_keyboard: Iterable[Iterable[tg_IKB]] | None = None,
            buttons: Sequence[tg_IKB] | None = None,
    ) -> list[list[tg_IKB]]:
        if inline_keyboard:
            buttons = cls.get_keyboard_buttons(inline_keyboard=inline_keyboard, )
        inline_keyboard = [buttons[i:i + btns_in_row] for i in range(0, len(buttons), btns_in_row)]
        return inline_keyboard


class ChoseKeyboardFabric:
    CHECKED_SYMBOL: str = '☑'
    UNCHECKED_SYMBOL: str = '🔲'
    Keyboard = CustomInlineKeyboardMarkup
    ALL_BTN_KEY = '0'

    def __init__(
            self,
            cbk_prefix: str,
            pattern: Pattern[str],
            all_btn_text: str | None = None,
            btns_in_row: int = 1,
            checked_symbol: str = CHECKED_SYMBOL,
            unchecked_symbol: str = UNCHECKED_SYMBOL,
            check_all_btn_key: str = ALL_BTN_KEY,
    ):
        self.btns_in_row = btns_in_row
        self.all_btn_text = all_btn_text
        self.checked_symbol = checked_symbol or self.CHECKED_SYMBOL
        self.unchecked_symbol = unchecked_symbol or self.UNCHECKED_SYMBOL
        self.cbk_prefix = cbk_prefix
        self.pattern = pattern
        self.all_btn_key = check_all_btn_key

    def get_cbk_key(self, cbk: str, ) -> str:
        return cbk[len(self.cbk_prefix) + 1:-2]  # +1, -2 - spaces

    def build_callback(self, cbk_key: str, is_chosen: bool, ) -> str:
        return f'{self.cbk_prefix} {cbk_key} {int(is_chosen)}'

    def build_button(
            self,
            text: str,
            cbk_key: str,
            is_chosen: bool = False,
            checkbox_on_left: bool = True,
            replace_old_symbol: bool = True,
    ) -> tg_IKB:
        """check symbol should be on the left if text too long"""
        if replace_old_symbol is True:
            text = text.replace(self.checked_symbol, '').replace(self.unchecked_symbol, '').strip()
        if is_chosen is True:
            if checkbox_on_left is True:
                text = f'{self.checked_symbol} {text}'
            else:
                text = f'{text} {self.checked_symbol}'
        elif is_chosen is False and self.unchecked_symbol:
            if checkbox_on_left:
                text = f'{self.unchecked_symbol} {text}'
            else:
                text = f'{text} {self.unchecked_symbol}'
        btn = tg_IKB(text=text, callback_data=self.build_callback(cbk_key=cbk_key, is_chosen=is_chosen, ), )
        return btn

    def create_btn_check_all(self, items: list[dict[Any, bool]], ) -> tg_IKB:
        """Don't use self.build_btn cuz symbol sign should be on another line side"""
        if all(item['is_chosen'] for item in items):
            return self.get_all_btn(is_chosen=True, )
        else:
            return self.get_all_btn(is_chosen=False, )

    def get_all_btn(
            self,
            text: str = '',
            cbk_key: str = '',
            is_chosen: bool = True,
            checkbox_on_left: bool = False,
    ) -> tg_IKB:
        return self.build_button(
            text=text or self.all_btn_text,
            cbk_key=cbk_key or self.all_btn_key,
            is_chosen=is_chosen,
            checkbox_on_left=checkbox_on_left,
        )

    def build(self, items: list[dict[Any, bool]], add_all_btn: bool = True, ) -> list[list[tg_IKB]]:
        keyboard = self.Keyboard.split(
            buttons=[self.build_button(**item, ) for item in items],
            btns_in_row=self.btns_in_row,
        )
        if add_all_btn:
            keyboard.append([self.create_btn_check_all(items=items, )])
        return keyboard

    @classmethod
    def extract_cbk_data(cls, cbk_data: Match[str], ) -> tuple[str, bool]:
        """
        split or groups - if cbk key contain more than 1 word - there 2 solutions
        1. "".join key somehow.
        2. create regex groups with brackets ().
        """
        _, cbk_payload, is_chosen = cbk_data.groups()
        return cbk_payload, not bool(int(is_chosen))  # not bool - inversion just in place (is this a right place?)

    def set_all_btns(self, keyboard: list[list[tg_IKB]], flag: bool, ) -> list[list[tg_IKB]]:
        """
        Set all buttons flags to True of False
        check_btn should handle safely the all_btn
        """
        for row_index, row in enumerate(keyboard):  # [:-1] if all_btn is a last row in keyboard
            for column_index, btn in enumerate(row):
                keyboard[row_index][column_index] = self.check_btn(btn=btn, flag=flag, )
        return keyboard

    def update_all_btn(self, keyboard: list[list[tg_IKB]], ) -> list[list[tg_IKB]]:
        """get selected and unselected items, build dict from it"""
        if not self.all_btn_text:
            return keyboard  # pragma: no cover
        # all_btn = keyboard[-1][-1]
        all_btn, all_btn_row_index, all_btn_column_index = self.Keyboard.find_btn_by_cbk(
            inline_keyboard=keyboard,
            cbk=f'{self.cbk_prefix} {self.all_btn_key}',
        )
        for row in keyboard:
            for btn in row:
                if btn.callback_data[-1] != '1' and btn != all_btn:
                    keyboard[all_btn_row_index][all_btn_column_index] = self.check_btn(btn=all_btn, flag=False, )
                    return keyboard
        keyboard[all_btn_row_index][all_btn_column_index] = self.check_btn(btn=all_btn, flag=True, )
        return keyboard

    def check_btn(self, btn: tg_IKB, flag: bool, ) -> tg_IKB:
        if btn.text.startswith(self.checked_symbol) or btn.text.startswith(self.unchecked_symbol):
            checkbox_on_left = True
        else:
            checkbox_on_left = False
        return self.build_button(
            text=btn.text,
            cbk_key=self.get_cbk_key(cbk=btn.callback_data, ),
            is_chosen=flag,
            checkbox_on_left=checkbox_on_left,
            replace_old_symbol=True,
        )

    def invert_btn(self, btn: tg_IKB, ) -> tg_IKB:
        if btn.callback_data[-1] == '0':
            return self.check_btn(btn=btn, flag=True, )
        else:
            return self.check_btn(btn=btn, flag=False, )

    def is_all_btn(self, cbk_data: str, ) -> bool:
        return (
                self.all_btn_text and
                cbk_data.split()[1] == self.all_btn_key and
                len(cbk_data.split()) == 3
        )

    def update_keyboard(self, btn_cbk_data: str, keyboard: tg_IKM, ) -> list[list[tg_IKB]]:
        """
        returns new keyboard cuz tg_IKM keyboard immutable in PTB.
        is_chosen param no need cuz current value from keyboard just will be negated
        """
        # TODO dirty, check if all btn pressed
        keyboard = self.Keyboard.to_list(inline_keyboard=keyboard.inline_keyboard, )
        if self.is_all_btn(cbk_data=btn_cbk_data, ):
            if btn_cbk_data.split()[-1] == '1':
                self.set_all_btns(keyboard=keyboard, flag=False, )
            else:
                self.set_all_btns(keyboard=keyboard, flag=True, )
        else:
            btn, row_index, column_index = self.Keyboard.find_btn_by_cbk(
                inline_keyboard=keyboard,
                cbk=btn_cbk_data,
            )
            keyboard[row_index][column_index] = self.invert_btn(btn=btn, )
        # new_keyboard = self.update_all_btn(keyboard=keyboard, )
        return keyboard
