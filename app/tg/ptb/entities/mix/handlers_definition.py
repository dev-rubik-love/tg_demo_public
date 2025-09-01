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

from telegram import Update
from telegram.ext import (
    TypeHandler,
    filters,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
)

from app.config import MAIN_ADMIN

from . import handlers, constants
from ..shared.handlers_definition import empty_cbk_handler, unknown_bot_cbk_handler

# from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    pass


def create_debug_logger() -> TypeHandler:
    result = TypeHandler(type=Update, callback=handlers.debug_logger, )
    return result


def create_typing_response() -> TypeHandler:
    result = TypeHandler(type=Update, callback=handlers.typing_response, )
    return result


def create_unknown_bot_handler() -> MessageHandler:
    result = MessageHandler(filters=filters.ChatType.PRIVATE, callback=handlers.unknown_handler, )
    return result


def create_analytics_handler() -> TypeHandler:
    result = TypeHandler(type=Update, callback=handlers.analytics_handler, )
    return result


def create_release_resources_handler() -> TypeHandler:
    result = TypeHandler(type=Update, callback=handlers.release_resources, )
    return result


def create_pickle_persistence_flush_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.PICKLE_FLUSH_S,
        filters=filters.User(user_id=MAIN_ADMIN),
        callback=handlers.pickle_persistence_flush_handler,
    )
    return result


# # # CMD # # #

def create_donate_cmd() -> CommandHandler:
    result = CommandHandler(command=constants.DONATE_S, callback=handlers.donate, )
    return result


def create_help_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.ALL_BOT_COMMANDS_S,
        callback=handlers.all_bot_commands_handler,
    )
    return result


def create_faq_cmd() -> CommandHandler:
    result = CommandHandler(command=constants.FAQ_S, callback=handlers.faq, )
    return result


def create_health_cmd() -> CommandHandler:
    result = CommandHandler(command=constants.HEALTH_S, callback=handlers.health, )
    return result


# # # CBK # # #
def create_hide_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(callback=handlers.hide, pattern=constants.Cbks.HIDE_R, )
    return result


# # # GEN # # #
def create_gen_bots_handler_cmd() -> CommandHandler:
    """Gen bots and votes too"""
    result = CommandHandler(
        command=constants.GEN_BOTS_S,
        callback=handlers.gen_bots_handler_cmd,
        filters=filters.User(user_id=MAIN_ADMIN),
    )
    return result


def create_gen_me_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=constants.GEN_ME_S,
        callback=handlers.gen_me_handler_cmd,
        filters=filters.User(user_id=MAIN_ADMIN),
    )
    return result


# PRE
debug_logger = create_debug_logger()
typing_response = create_typing_response()
# POST
analytics_handler = create_analytics_handler()
unknown_bot_handler = create_unknown_bot_handler()
release_resources = create_release_resources_handler()
# CMD
help_handler_cmd = create_help_cmd()
faq_handler_cmd = create_faq_cmd()
health_handler_cmd = create_health_cmd()
donate_handler_cmd = create_donate_cmd()
pickle_persistence_flush_handler_cmd = create_pickle_persistence_flush_cmd()
# CBK
hide_cbk_handler = create_hide_cbk_handler()
# GEN
gen_bots_handler_cmd = create_gen_bots_handler_cmd()
gen_me_handler_cmd = create_gen_me_handler_cmd()

available_handlers = {
    -10: (debug_logger,),
    -9: (typing_response,),
    0: (
        help_handler_cmd,
        faq_handler_cmd,
        health_handler_cmd,
        hide_cbk_handler,
        donate_handler_cmd,
        gen_bots_handler_cmd,
        gen_me_handler_cmd,
        pickle_persistence_flush_handler_cmd,
    ),
    8: (empty_cbk_handler, ),
    9: (analytics_handler,),
    10: (release_resources,),
}

unknown_handlers = (unknown_bot_handler, unknown_bot_cbk_handler, )