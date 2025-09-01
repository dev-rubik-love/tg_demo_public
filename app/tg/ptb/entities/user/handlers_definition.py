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
    CommandHandler,
    ConversationHandler,
)

from . import handlers
from .constants import REG_S
from ..shared.handlers_definition import cancel_handler, DEFAULT_CH_TIMEOUT

# from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    pass


class RegistrationCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=REG_S,
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
    def create_name_handler():
        name_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.name_handler,
        )
        return name_handler

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
    def create_location_handler_geo():
        location_handler_geo = MessageHandler(
            filters=filters.LOCATION,
            callback=handlers.location_handler_geo,
        )
        return location_handler_geo

    @staticmethod
    def create_location_handler_text():
        location_handler_text = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.location_handler_text,
        )
        return location_handler_text

    @staticmethod
    def create_photos_handler_photo():
        photos_handler_tg_photo = MessageHandler(
            filters=filters.PHOTO,
            callback=handlers.photos_handler_tg_photo,
        )
        return photos_handler_tg_photo

    @staticmethod
    def create_photos_handler_text():
        photos_handler_text = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.photos_handler_text,
        )
        return photos_handler_text

    @staticmethod
    def create_comment_handler():
        comment_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.comment_handler,
        )
        return comment_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=filters.TEXT,
            callback=handlers.confirm_handler,
        )
        return confirm_handler

    cancel_handler = cancel_handler
    entry_point = create_entry_point()
    entry_point_handler = create_entry_point_handler()
    name_handler = create_name_handler()
    goal_handler = create_goal_handler()
    gender_handler = create_gender_handler()
    age_handler = create_age_handler()
    location_handler_geo = create_location_handler_geo()
    location_handler_text = create_location_handler_text()
    photos_handler_photo = create_photos_handler_photo()
    photos_handler_text = create_photos_handler_text()
    comment_handler = create_comment_handler()
    confirm_handler = create_confirm_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point],

            #  prefallbacks=[cls.cancel, ],
            states={
                0: [cls.cancel_handler, cls.entry_point_handler, ],
                1: [cls.cancel_handler, cls.name_handler, ],
                2: [cls.cancel_handler, cls.goal_handler, ],
                3: [cls.cancel_handler, cls.gender_handler, ],
                4: [cls.cancel_handler, cls.age_handler, ],
                5: [cls.cancel_handler, cls.location_handler_geo, cls.location_handler_text],
                6: [cls.cancel_handler, cls.photos_handler_photo, cls.photos_handler_text, ],
                7: [cls.cancel_handler, cls.comment_handler],
                8: [cls.cancel_handler, cls.confirm_handler],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,  # See 2
            allow_reentry=True,
            name='registration'
        )
        if set_ch is True:
            cls.CH = result
        return result


# CH
registration_ch = RegistrationCH.create_ch()

available_handlers = (registration_ch, )
