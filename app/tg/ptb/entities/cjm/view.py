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

from telegram import (
    ReplyKeyboardMarkup as tg_RKM,
)

from . import texts
from ..shared.view import SharedInit, Shared
from ..shared.texts import FOR_READY
from ..match.constants import Cmds as SearchCmds
from ..collection.view import Keyboards as CollectionKeyboards

if TYPE_CHECKING:
    from telegram import Message
    from app.tg.ptb.entities.user.model import IUser
    from app.tg.ptb.entities.collection.view import Collections as CollectionsView
    from app.tg.ptb.entities.collection.model import ICollection

"""
Customer Journey Map (modes / use cases)
"""


class Cjm(SharedInit, ):

    def __init__(self, user: IUser, collections_view: CollectionsView, shared_view: Shared, ):
        super().__init__(user=user, )
        self.collections_view = collections_view
        self.shared = shared_view

    async def start_mode(self, ) -> Message:
        sent_message = await self.bot.send_message(
            chat_id=self.id,
            text=texts.START_MODE,
            reply_markup=Keyboards.start_mode,
        )
        return sent_message

    async def public_mode_show_collections(self, collections: list[ICollection], ) -> Message:
        """Show collections to sender"""
        await self.shared.easter_egg()  # Usability, remove old keyboard (even if already hidden)
        return await self.collections_view.show_collections(
            collections=collections,
            text=f'{texts.PUBLIC_MODE}\n{FOR_READY.format(READY=SearchCmds.SEARCH)}',
            keyboard=CollectionKeyboards.Inline.ShowCollections,
        )

    async def public_mode_notify_ready_keyword(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=FOR_READY.format(READY=SearchCmds.SEARCH, ),
            reply_markup=Keyboards.search_cmd_btn,
        )

    async def personal_mode_show_collections(self, collections: list[ICollection], ) -> Message:
        """Show collections to sender"""
        await self.shared.easter_egg()  # Usability, remove old keyboard (even if already hidden)
        text = texts.PERSONAL_MODE
        if len(collections) > 8:  # If many posts user may miss for ready notification. 8 is just approximate number.
            text = f'{texts.PERSONAL_MODE}\n{FOR_READY}'
        return await self.collections_view.show_collections(
            collections=collections,
            text=text,
            keyboard=CollectionKeyboards.Inline.MarkAndShow,
        )

    remove_sharing_message = Shared.remove_sharing_message


class Keyboards:
    start_mode = tg_RKM(
        keyboard=[[texts.Cmds.PERSONAL_MODE], [texts.Cmds.PUBLIC_MODE]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    search_cmd_btn = tg_RKM(
        [[SearchCmds.SEARCH]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
