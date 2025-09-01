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
from ..shared.handlers_definition import cancel_handler, show_profile_cbk_handler, DEFAULT_CH_TIMEOUT

# from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    pass

"""
1. https://stackoverflow.com/a/61275118/11277611
2. Value in seconds for dropping db connection and user temporary tables
"""


def create_share_collections_ch() -> ConversationHandler:
    result = ConversationHandler(

        #  prefallbacks=[
        #     MessageHandler(
        #         filters=constants.Regexp.CANCEL_R,
        #         callback=create_cancel().callback,
        #     ),
        # ],

        entry_points=[
            CommandHandler(
                command=constants.SHARE_COLLECTIONS_S,
                callback=handlers.SharePersonalCollections.entry_point,
            )],

        states={
            0: [
                cancel_handler,
                CallbackQueryHandler(
                    callback=handlers.SharePersonalCollections.mark_to_share_cbk_handler,
                    pattern=constants.Cbks.MARK_COLLECTION_R,
                ),
                MessageHandler(
                    filters=filters.TEXT,
                    callback=handlers.SharePersonalCollections.continue_handler,
                ),
            ],
            1: [
                cancel_handler,
                MessageHandler(
                    filters=filters.ALL,
                    callback=handlers.SharePersonalCollections.recipient_handler,
                ),
            ],
        },
        fallbacks=[],
        conversation_timeout=DEFAULT_CH_TIMEOUT,
        allow_reentry=True,
        name='share_collections',
        persistent=PERSISTENT,
    )
    return result


def create_accept_share_collections_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.SharePersonalCollections.recipient_decision_cbk_handler,
        pattern=constants.Cbks.ACCEPT_COLLECTIONS_R,
    )
    return result


def create_show_collection_posts_to_recipient_cbk_handler() -> CallbackQueryHandler:
    """
    Especially for personal mode posts sharing cuz posts cbk handler for public and personal mode are different
    """
    result = CallbackQueryHandler(
        callback=handlers.SharePersonalCollections.show_collection_posts_to_recipient_cbk_handler,
        pattern=constants.Cbks.SHOW_SHARED_COLLECTION_POSTS_R,
    )
    return result


def create_show_collection_posts_cbk_handler() -> CallbackQueryHandler:
    """
    Especially for personal mode posts sharing cuz posts cbk handler for public and personal mode are different
    """
    result = CallbackQueryHandler(
        callback=handlers.show_collection_posts_cbk_handler,
        pattern=constants.Cbks.SHOW_COLLECTION_POSTS_R,
    )
    return result


def create_get_my_collections_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.GET_MY_COLLECTIONS_S,
        callback=handlers.get_my_collections_handler_cmd,
    )
    return result


accept_share_collections_cbk = create_accept_share_collections_cbk_handler()

show_collection_posts_cbk = create_show_collection_posts_cbk_handler()
show_collection_posts_to_recipient_cbk_handler = create_show_collection_posts_to_recipient_cbk_handler()
share_collections_ch = create_share_collections_ch()
get_my_collections_cmd = create_get_my_collections_handler_cmd()

available_handlers = (
    accept_share_collections_cbk,
    show_profile_cbk_handler,
    show_collection_posts_cbk,
    show_collection_posts_to_recipient_cbk_handler,
    share_collections_ch,
    get_my_collections_cmd,
)
