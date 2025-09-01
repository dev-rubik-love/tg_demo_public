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
from typing import TYPE_CHECKING

from telegram import ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.error import TelegramError

from app.config import DONATE_IMAGE_PATH
from . import texts
from ..shared.view import SharedInit
from ..texts import PUBLIC_COMMANDS

if TYPE_CHECKING:
    from telegram import Message


class Mix(SharedInit, ):

    async def donate(self, ) -> Message:
        return await self.bot.send_photo(
            chat_id=self.id,
            photo=DONATE_IMAGE_PATH,
            caption=texts.DONATE,
        )

    async def unknown_handler(self, reply_to_message_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=f'{texts.MISUNDERSTAND}\n\n{texts.CmdDescriptions.HERE_COMMANDS}\n{PUBLIC_COMMANDS}',
            reply_to_message_id=reply_to_message_id,
        )

    async def show_bot_commands(self, ) -> Message:
        """Repeat TG bot description from a local obj"""
        return await self.bot.send_message(chat_id=self.id, text=PUBLIC_COMMANDS, )

    async def show_bot_commands_remote(self, ) -> Message:
        """Repeat TG bot description from the server"""
        remote_commands = await self.bot.get_my_commands()
        commands = ''.join([f"/{command.command} - {command.description}\n" for command in remote_commands])
        text = f'{texts.CmdDescriptions.HERE_COMMANDS}\n\n{commands}'
        return await self.bot.send_message(chat_id=self.id, text=text, )

    async def faq(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=texts.FAQ,
            parse_mode=ParseMode.HTML,
        )

    async def drop_hide_btn(self, message_ids: list[int], ) -> None:
        """Create "hide" btn "hide" text message"""
        for message_id in message_ids:
            try:
                await self.bot.delete_message(chat_id=self.id, message_id=message_id, )
            except TelegramError:  # pragma: no cover
                continue


class Keyboards:
    remove = ReplyKeyboardRemove
