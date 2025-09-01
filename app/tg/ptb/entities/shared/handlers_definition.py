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

from telegram.ext import MessageHandler, filters, CallbackQueryHandler

from . import handlers, constants

if TYPE_CHECKING:
    pass

# 1. https://stackoverflow.com/a/61275118/11277611
# 2. Value in seconds for dropping db connection and user temporary tables
DEFAULT_CH_TIMEOUT = 3600


def create_cancel_handler() -> MessageHandler:
    cancel = MessageHandler(
        callback=handlers.cancel,
        filters=filters.Regex(pattern=constants.CANCEL_R, ),
    )
    return cancel


def create_empty_cbk_handler() -> CallbackQueryHandler:
    """Just do nothing on click"""
    result = CallbackQueryHandler(
        callback=handlers.unclickable_cbk_handler,
        pattern=constants.EMPTY_CBK_R,
    )
    return result


def create_unknown_cbk_handler() -> CallbackQueryHandler:
    """Just do nothing on click"""
    result = CallbackQueryHandler(callback=handlers.unknown_cbk_handler, )
    return result


show_profile_cbk_handler = CallbackQueryHandler(
    callback=handlers.show_profile_cbk_handler,
    pattern=constants.SHOW_PROFILE_R,
)
empty_cbk_handler = create_empty_cbk_handler()
unknown_bot_cbk_handler = create_unknown_cbk_handler()
cancel_handler = create_cancel_handler()
