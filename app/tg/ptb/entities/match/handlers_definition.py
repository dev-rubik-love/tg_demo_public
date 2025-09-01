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
from ..shared.handlers_definition import cancel_handler, DEFAULT_CH_TIMEOUT

# from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    pass


def create_personal_example_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.PERSONAL_EXAMPLE_S,
        callback=handlers.personal_example,
    )
    return result


class GetStatisticWithCH:

    @staticmethod
    def create_entry_point() -> CommandHandler:
        entry_point = CommandHandler(
            command=constants.GET_STATISTIC_WITH_S,
            callback=handlers.GetStatisticWith.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler() -> MessageHandler:
        entry_point_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.GetStatisticWith.entry_point_handler,
        )
        return entry_point_handler

    entry_point = create_entry_point()
    entry_point_handler = create_entry_point_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            #  prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={0: [cancel_handler, cls.entry_point_handler], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='get_statistic_with',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = result
        return result


class SearchCH:

    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=constants.SEARCH_S,
            callback=handlers.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler():
        entry_point_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.entry_point_handler,
        )
        return entry_point_handler

    @staticmethod
    def create_channel_sources_cbk_handler():
        channel_sources_cbk_handler = CallbackQueryHandler(
            pattern=constants.Cbks.CHOOSE_CHANNELS_R,
            callback=handlers.channel_sources_cbk_handler,
        )
        return channel_sources_cbk_handler

    @staticmethod
    def create_goal_handler():
        goal_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.goal_handler,
        )
        return goal_handler

    @staticmethod
    def create_gender_handler():
        gender_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.gender_handler,
        )
        return gender_handler

    @staticmethod
    def create_age_handler():
        age_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.age_handler,
        )
        return age_handler

    @staticmethod
    def create_checkbox_cbk_handler():
        checkbox_cbk_handler = CallbackQueryHandler(
            callback=handlers.checkbox_cbk_handler,
            pattern=constants.Cbks.CHECKBOX_R,
        )
        return checkbox_cbk_handler

    @staticmethod
    def create_checkboxes_handler():
        checkboxes_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.checkboxes_handler,
        )
        return checkboxes_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.match_type_handler,
        )
        return confirm_handler

    @staticmethod
    def create_show_match_handler():
        show_match_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.show_match_handler,
        )
        return show_match_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    entry_point_handler = create_entry_point_handler()
    channel_sources_cbk_handler = create_channel_sources_cbk_handler()
    goal_handler = create_goal_handler()
    gender_handler = create_gender_handler()
    age_handler = create_age_handler()
    checkbox_cbk_handler = create_checkbox_cbk_handler()
    checkboxes_handler = create_checkboxes_handler()
    confirm_handler = create_confirm_handler()
    show_match_handler = create_show_match_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point, ],
            #  prefallbacks=[cls.cancel, ],
            states={
                0: [cls.cancel_handler, cls.entry_point_handler, cls.channel_sources_cbk_handler, ],
                1: [cls.cancel_handler, cls.goal_handler, cls.channel_sources_cbk_handler, ],
                2: [cls.cancel_handler, cls.gender_handler, ],
                3: [cls.cancel_handler, cls.age_handler, ],
                4: [cls.cancel_handler, cls.checkbox_cbk_handler, cls.checkboxes_handler, ],
                5: [cls.cancel_handler, cls.confirm_handler, ],
                6: [cls.cancel_handler, cls.show_match_handler, ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='search',
            persistent=PERSISTENT,
        )
        if set_ch is True:
            cls.CH = result
        return result


get_statistic_with_ch = GetStatisticWithCH.create_ch()
search_ch = SearchCH.create_ch()
personal_example_cmd = create_personal_example_handler_cmd()

available_handlers = (
    get_statistic_with_ch,
    search_ch,
    personal_example_cmd,
)
