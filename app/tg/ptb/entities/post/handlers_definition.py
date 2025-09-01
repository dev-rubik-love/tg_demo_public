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

from telegram.ext import (
    filters,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from app.config import PERSISTENT

from . import handlers, constants
from ..collection.constants import Cbks as CollectionCbks
from ..shared.handlers_definition import cancel_handler, DEFAULT_CH_TIMEOUT


def create_request_personal_post_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.RequestPersonalPosts.recipient_decision_cbk_handler,
        pattern=constants.Cbks.REQUEST_PERSONAL_POSTS_R,
    )
    return result


def create_update_public_post_status_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=handlers.update_public_post_status_cbk,
        pattern=constants.Cbks.UPDATE_PUBLIC_POST_STATUS_R,
    )
    return result


def create_get_public_post_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.GET_PUBLIC_POST_S,
        callback=handlers.get_public_post,
    )
    return result


def create_get_my_personal_posts_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.GET_MY_PERSONAL_POSTS_S,
        callback=handlers.get_my_personal_posts,
    )
    return result


def create_share_personal_post_cbk_handler() -> CallbackQueryHandler:  # Rename to posts
    result = CallbackQueryHandler(
        callback=handlers.SharePersonalPosts.recipient_decision_cbk_handler,
        pattern=constants.Cbks.ACCEPT_PERSONAL_POSTS_R,
    )
    return result


class CreatePublicPostCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            # START_S need for inline mode, TG automatically adds "/start" cmd as prefix in this mode
            command=(constants.CREATE_PUBLIC_POST_S, constants.START_S,),
            callback=handlers.CreatePublicPost.entry_point,
            filters=filters.Regex(constants.Regex.CREATE_PUBLIC_POST),
            # has_args=True,  # No need cuz it will definitely requre the args after command
        )
        return entry_point

    @staticmethod
    def create_sample_handler():
        sample_handler = MessageHandler(
            filters=filters.ALL,
            callback=handlers.CreatePublicPost.sample_handler,
        )
        return sample_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.CreatePublicPost.confirm_handler,
        )
        return confirm_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    sample_handler = create_sample_handler()
    confirm_handler = create_confirm_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            entry_points=[cls.entry_point],
            #  prefallbacks=[cls.cancel],
            states={
                0: [cls.cancel_handler, cls.sample_handler, ],
                1: [cls.cancel_handler, cls.confirm_handler, ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='create_public_post',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = ch
        return ch


class CreatePersonalPostCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=constants.CREATE_PERSONAL_POST_S,
            callback=handlers.CreatePersonalPost.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler():
        entry_point_handler = MessageHandler(
            filters=filters.ALL,
            callback=handlers.CreatePersonalPost.entry_point_handler,
        )
        return entry_point_handler

    @staticmethod
    def create_sample_handler():
        sample_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.CreatePersonalPost.post_sample_handler,
        )
        return sample_handler

    @staticmethod
    def create_collections_handler():
        collections_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.CreatePersonalPost.collection_names_text_handler,
        )
        return collections_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=filters.Regex(pattern=handlers.CreatePersonalPost.READY_R, ),
            callback=handlers.CreatePersonalPost.confirm_handler,
        )
        return confirm_handler

    @staticmethod
    def create_collection_name_cbk_handler():
        confirm_handler = CallbackQueryHandler(
            callback=handlers.CreatePersonalPost.collection_name_cbk_handler,
            pattern=CollectionCbks.CHOOSE_COLLECTION_R,  # Post or collection scope should be?
        )
        return confirm_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    entry_point_handler = create_entry_point_handler()
    sample_handler = create_sample_handler()
    collections_handler = create_collections_handler()
    confirm_handler = create_confirm_handler()
    collection_name_cbk_handler = create_collection_name_cbk_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            #  prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={
                0: [cls.cancel_handler, cls.entry_point_handler, ],
                1: [cls.cancel_handler, cls.sample_handler, ],
                2: [
                    cls.cancel_handler,
                    cls.confirm_handler,  # confirm_handler should be before collections_handler
                    cls.collections_handler,
                    cls.collection_name_cbk_handler,
                ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='create_personal_post',
            persistent=PERSISTENT,
        )

        if set_ch is True:
            cls.CH = ch
        return ch


class SharePersonalPostsCh:

    @staticmethod
    def create_entry_point() -> CommandHandler:
        entry_point = CommandHandler(
            command=constants.SHARE_PERSONAL_POSTS_S,
            callback=handlers.SharePersonalPosts.entry_point,
        )
        return entry_point

    @staticmethod
    def create_recipient_handler() -> MessageHandler:
        recipient_handler = MessageHandler(
            filters=filters.ALL,
            callback=handlers.SharePersonalPosts.recipient_handler,
        )
        return recipient_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    recipient_handler = create_recipient_handler()
    CH = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(

            #  prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={0: [cls.cancel_handler, cls.recipient_handler, ], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='share_personal_posts',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = ch
        return ch


class RequestPersonalPostsCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=constants.REQUEST_PERSONAL_POSTS_S,
            callback=handlers.RequestPersonalPosts.entry_point,
        )
        return entry_point

    @staticmethod
    def create_recipient_handler():
        recipient_handler = MessageHandler(
            filters=filters.ALL,
            callback=handlers.RequestPersonalPosts.recipient_handler,
        )
        return recipient_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    recipient_handler = create_recipient_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            entry_points=[cls.entry_point, ],
            #  prefallbacks=[cls.cancel, ],
            states={0: [cls.cancel_handler, cls.recipient_handler, ], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='request_personal_posts',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = ch
        return ch


# CH
public_post_ch = CreatePublicPostCH.create_ch()
personal_post_ch = CreatePersonalPostCH.create_ch()
share_personal_posts_ch = SharePersonalPostsCh.create_ch()
request_personal_posts_ch = RequestPersonalPostsCH.create_ch()
# CMD
get_public_post_cmd = create_get_public_post_cmd()
get_my_personal_posts_cmd = create_get_my_personal_posts_cmd()
# CBK
share_personal_posts_cbk = create_share_personal_post_cbk_handler()
request_personal_post_cbk = create_request_personal_post_cbk_handler()
update_public_post_status_cbk = create_update_public_post_status_cbk_handler()

available_handlers = (
    # CMD
    get_public_post_cmd,
    get_my_personal_posts_cmd,
    # CBK
    share_personal_posts_cbk,
    request_personal_post_cbk,
    update_public_post_status_cbk,
    # CH
    public_post_ch,
    personal_post_ch,
    share_personal_posts_ch,
    request_personal_posts_ch,
)
