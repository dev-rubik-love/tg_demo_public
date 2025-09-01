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
from pprint import pformat as pprint_pformat
from typing import TYPE_CHECKING
from datetime import datetime as datetime_datetime, timezone as datetime_timezone
from collections.abc import Iterable

from httpx import ConnectTimeout
from telegram.constants import ChatAction
from rubik_core.db.manager import Postgres
from rubik_core.shared.utils import get_num_from_text, limit_num, LazyValue

from app.config import GRASPIL_ANALYTICS_API_KEY
from app.postconfig import app_logger, graspil_logger, httpx_client
from app.entities.shared.exceptions import KnownException

from .services import System as SystemService
from ..collection.services import Collection as CollectionService

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


async def faq(_: Update, context: CallbackContext, ):
    await context.view.mix.faq()


async def health(_: Update, context: CallbackContext, ):
    await context.view.say_ok()


async def donate(_: Update, context: CallbackContext, ):
    await context.view.mix.donate()


async def unknown_handler(update: Update, context: CallbackContext, ):
    await context.view.mix.unknown_handler(reply_to_message_id=update.effective_message.message_id, )


async def pickle_persistence_flush_handler(_: Update, context: CallbackContext, ):
    """
    Will be saved after stopping the application, not after the command
    Bot are not serializable
    """
    await context.application.persistence.flush()
    await context.view.say_ok()


async def hide(update: Update, context: CallbackContext, ):
    _, *message_ids = update.callback_query.data.split()
    await context.view.mix.drop_hide_btn(message_ids=[int(message_id) for message_id in message_ids], )


async def all_bot_commands_handler(_: Update, context: CallbackContext, ):
    await context.view.mix.show_bot_commands()


async def debug_logger(update: Update, context: CallbackContext, ):
    log_data = {
        "message_text": getattr(update.effective_message, 'text', None),
        "message_attachment": getattr(update.effective_message, 'effective_attachment', None),
        "callback_data": getattr(update.callback_query, 'data', None),
        "user_data": context.user_data or None,
        "chat_data": context.chat_data or None,
        "bot_data": context.bot_data or None,
    }
    app_logger.debug('\n' + pprint_pformat({k: v for k, v in log_data.items() if v}))


async def gen_bots_handler_cmd(update: Update, context: CallbackContext, ):
    num = get_num_from_text(text=update.effective_message.text)
    if num is None:
        await context.view.warn.nan_help_msg()
        return
    num_to_gen = limit_num(num=num, min_num=1, max_num=99, )
    SystemService.create_bots(bots_ids=list(range(1, num_to_gen + 1)), )
    await context.view.say_ok()


async def gen_me_handler_cmd(update: Update, context: CallbackContext, ):
    # Gen bot func to gen me
    SystemService.create_bots(bots_ids=[update.effective_user.id, ], )
    default_personal_collections = CollectionService.get_defaults(
        prefix=CollectionService.NamePrefix.PUBLIC,
    )
    for collection in default_personal_collections:  # Set votes for default posts
        posts = collection.get_posts(collection_id=collection.id, connection=context.connection, )
        for post in posts:
            context.user.set_vote(
                vote=SystemService.generator.gen_vote(user=context.user, post=post, ),
                post=post,
            )
    await context.view.say_ok()


async def typing_response(update: Update, context: CallbackContext, ):
    """
    Imitate typing dots on any user input.
    Notice: three dots animation indicator will be on top of the chat, not in the text input field,
    this is how TG works.
    """
    # Better move to view
    try:
        if chat_id := (getattr(update.effective_chat, 'id', None) or update.effective_user.id):
            await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING, )
    except Exception as e:
        app_logger.error(msg=e, exc_info=True, )


async def error_handler(update: Update | None, context: CallbackContext, ) -> None:
    # Note: update may be None
    """
    Log the error and send a telegram message to notify the developer.
    The error won’t show up in the logger, so you need to reraise the error for that.
    """
    if isinstance(context.error, KnownException):
        return  # pragma: no cover:
    app_logger.error(msg=context.error, exc_info=context.error, )
    if getattr(update, 'inline_query'):  # No need to answer on queries from inline mode
        return  # pragma: no cover
    elif context.user_data:  # user_data not exists if update produced not by the user (another bot for example)
        if cbk := getattr(update, 'callback_query', None):  # If btn was pressed
            await context.view.internal_error(tooltip=cbk, )
        else:
            await context.view.internal_error()


async def analytics_handler(update: Update, _: CallbackContext):
    # TODO send batches up to 1000 updates
    try:
        await httpx_client.post(
            url="https://api.graspil.ru/api/send-batch-update",
            headers={
                'Content-Type': 'application/json',
                'Api-Key': GRASPIL_ANALYTICS_API_KEY,
            },
            json=[
                {
                    # API requires such time format, example: '2024-08-03T20:00:00.123+02:00'
                    "date": datetime_datetime.now(datetime_timezone.utc).isoformat(timespec='milliseconds'),
                    "update": update.to_dict(),  # to_dict exactly
                },
            ],
        )
    except ConnectTimeout:
        graspil_logger.error(msg=f'Graspil ConnectTimeout: {ConnectTimeout}', exc_info=False, )
    except Exception as e:
        app_logger.error(msg=e, exc_info=True, )


async def release_resources(_: Update, context: CallbackContext, ):
    """
    Call after every update
    Don't use drop_user_data cuz it will clear the data of CHs
    context.application.drop_user_data(user_id=context.user.id, )
    """
    try:
        # getattr if LazeValue was passed; A bit dirty but ok
        if isinstance(context.connection, LazyValue):
            context.connection.set()
            Postgres.connection_pool.putconn(conn=context.connection.value, )
        else:
            Postgres.connection_pool.putconn(conn=context.connection, )
        # don't drop connection if user inside the search CH (forms.target as indicator)
        if not (context.user_data and getattr(context.user_data.forms, 'target', None)):
            context.connection = None
    except Exception as e:
        app_logger.error(msg=e, exc_info=True, )
