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

from pytest import mark as pytest_mark

from app.tg.ptb.entities.cjm import view

from app.tg.ptb.entities.match.texts import Cmds as MatchCmds

if TYPE_CHECKING:
    from unittest.mock import MagicMock


async def test_start_mode(mock_view_f: MagicMock, ):
    result = await view.Cjm.start_mode(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.texts.START_MODE.format(view.texts.Cmds.PERSONAL_MODE, view.texts.Cmds.PUBLIC_MODE, ),
        reply_markup=view.Keyboards.start_mode,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_public_mode_show_collections(mock_view_f: MagicMock, ):
    """Show collections to sender"""
    result = await view.Cjm.public_mode_show_collections(self=mock_view_f.cjm, collections=['foo'], )
    mock_view_f.cjm.collections_view.show_collections.acow(
        text=f'{view.texts.PUBLIC_MODE}\n{view.texts.FOR_READY.format(READY=MatchCmds.SEARCH)}',
        collections=['foo'],
        keyboard=view.CollectionKeyboards.Inline.ShowCollections,
    )
    assert result == mock_view_f.cjm.collections_view.show_collections.return_value


async def test_public_mode_notify_ready_keyword(mock_view_f: MagicMock, ):
    """Show collections to sender"""
    result = await view.Cjm.public_mode_notify_ready_keyword(self=mock_view_f.cjm, )
    mock_view_f.cjm.bot.send_message.acow(
        chat_id=mock_view_f.cjm.id,
        text=view.texts.FOR_READY.format(READY=MatchCmds.SEARCH, ),
        reply_markup=view.Keyboards.search_cmd_btn,
    )
    assert result == mock_view_f.cjm.bot.send_message.return_value


@pytest_mark.parametrize(
    argnames=('collections', 'text'),
    argvalues=(  # Different text for different collection len
            (['foo'], view.texts.PERSONAL_MODE),
            (['foo'] * 10, f'{view.texts.PERSONAL_MODE}\n{view.texts.FOR_READY}'),
    ), )
async def test_personal_mode(mock_view_f: MagicMock, text: str, collections: list[str], ):
    result = await view.Cjm.personal_mode_show_collections(self=mock_view_f.cjm, collections=collections, )
    mock_view_f.cjm.collections_view.show_collections.acow(
        text=text,
        collections=collections,
        keyboard=view.CollectionKeyboards.Inline.MarkAndShow,
    )
    assert result == mock_view_f.cjm.collections_view.show_collections.return_value
