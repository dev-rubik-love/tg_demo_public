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

from telegram.ext import ConversationHandler

from . import texts
from ..user.model import User

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


async def cancel(_: Update, context: CallbackContext, ):  # Common handler for all conversations to cancel them
    await context.view.cancel()
    return ConversationHandler.END


async def unclickable_cbk_handler(update: Update, context: CallbackContext, ):
    await context.view.unclickable_button(tooltip=update.callback_query, )


async def unknown_cbk_handler(update: Update, context: CallbackContext, ):
    await context.view.unknown_button(tooltip=update.callback_query, )


async def show_profile_cbk_handler(update: Update, context: CallbackContext, ):
    show_to_id = int(update.callback_query.data.split(' ')[-1])
    user = User(id=show_to_id, )
    user.load()  # TODO move to init
    if user.is_registered:
        await context.view.match.Profile(
            bot=context.bot,
            data_source=user,
            id=show_to_id
        ).send(show_to_id=update.callback_query.from_user.id, )
        await update.callback_query.answer()
    else:
        await update.callback_query.answer(text=texts.USER_NOT_REGISTERED, show_alert=True, )
