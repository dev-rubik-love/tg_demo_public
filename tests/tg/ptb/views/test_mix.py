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

from telegram.constants import ParseMode
from telegram import BotCommand

from app.tg.ptb.entities.mix.view import Mix as View, DONATE_IMAGE_PATH
from app.tg.ptb.entities.mix import texts
from app.tg.ptb.entities.texts import PUBLIC_COMMANDS

if TYPE_CHECKING:
    from unittest.mock import MagicMock


async def test_unknown_handler(mock_view_f: MagicMock, ):
    result = await View.unknown_handler(self=mock_view_f, reply_to_message_id=1, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{texts.MISUNDERSTAND}\n\n{texts.CmdDescriptions.HERE_COMMANDS}\n{PUBLIC_COMMANDS}',
        reply_to_message_id=1,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_bot_commands(mock_view_f: MagicMock, ):
    result = await View.show_bot_commands(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=PUBLIC_COMMANDS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_bot_commands_remote(mock_view_f: MagicMock, ):
    mock_view_f.bot.get_my_commands.return_value = (
        BotCommand(command='foo', description='123'),
        BotCommand(command='bar', description='456'),
    )
    result = await View.show_bot_commands_remote(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{texts.CmdDescriptions.HERE_COMMANDS}\n\n/foo - 123\n/bar - 456\n',
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_faq(mock_view_f: MagicMock, ):
    result = await View.faq(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=texts.FAQ,
        parse_mode=ParseMode.HTML,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_donate(mock_view_f: MagicMock, ):
    result = await View.donate(self=mock_view_f, )
    mock_view_f.bot.send_photo.acow(chat_id=mock_view_f.id, caption=texts.DONATE, photo=DONATE_IMAGE_PATH, )
    assert result == mock_view_f.bot.send_photo.return_value


async def test_drop_hide_btn(mock_view_f: MagicMock, ):
    await View.drop_hide_btn(self=mock_view_f, message_ids=[1, ], )
    mock_view_f.bot.delete_message.acow(chat_id=mock_view_f.id, message_id=1, )
