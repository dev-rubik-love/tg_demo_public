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

from telegram.ext import (
    filters,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from app.config import PERSISTENT

from . import handlers, constants
from ..collection import handlers as collection_handlers
from ..shared.handlers_definition import cancel_handler, DEFAULT_CH_TIMEOUT

# from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    pass


def create_public_mode_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.PUBLIC_MODE_S,
        callback=handlers.public_mode_cmd,
    )
    return result


class PersonalModeCH:

    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=constants.PERSONAL_MODE_S,
            callback=handlers.PersonalMode.entry_point,
        )
        return entry_point

    @staticmethod
    def create_show_collections_cbk_handler():
        """Show all collections and set cbk to mark some of them"""
        show_collections_handler = CallbackQueryHandler(
            callback=handlers.PersonalMode.show_collection_posts_to_sender_cbk_handler,
            pattern=constants.Cbks.MARK_SHOW_COLLECTION_R,
        )
        return show_collections_handler

    @staticmethod
    def create_continue_handler():
        continue_handler = MessageHandler(
            filters=filters.TEXT,
            callback=collection_handlers.SharePersonalCollections.continue_handler,
        )
        return continue_handler

    @staticmethod
    def create_recipient_handler():
        recipient_handler = MessageHandler(
            filters=filters.TEXT,
            callback=collection_handlers.SharePersonalCollections.recipient_handler,
        )
        return recipient_handler

    entry_point = create_entry_point()
    show_collections_cbk_handler = create_show_collections_cbk_handler()
    recipient_handler = create_recipient_handler()
    continue_handler = create_continue_handler()
    CH = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point, ],
            #  prefallbacks=[cls.cancel, ],
            states={
                0: [cancel_handler, cls.show_collections_cbk_handler, cls.continue_handler, ],
                1: [cancel_handler, cls.recipient_handler, ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='personal_mode',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = result
        return result


def create_start_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.START_S,
        callback=handlers.start_cmd,
        # Cmd sent from inline mode will contain '/start'  text automatically (/start reg for example),
        # but should be handled with arg (reg) handler only
        filters=filters.Regex(pattern=constants.NO_SPACE_R, ),
    )
    return result


start_handler_cmd = create_start_handler_cmd()
public_mode_cmd = create_public_mode_cmd()
personal_mode_ch = PersonalModeCH.create_ch()

available_handlers = (
    start_handler_cmd,
    public_mode_cmd,
    personal_mode_ch,
)
