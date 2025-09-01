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

from app.postconfig import known_exceptions_logger
from app.entities.shared.exceptions import PostNotFound, UnknownPostType

from .custom import accept_user as custom_accept_user, request_user as custom_request_user
from .entities.vote.constants import Cbks as VoteCbks
from .entities.shared.texts import Words as SharedWords
from .entities.post.model import ChannelPublicPost, BotPublicPost, PersonalPost

if TYPE_CHECKING:
    from custom_ptb.callback_context import CallbackContext as CallbackContext
    from telegram import Update, SharedUser


async def extract_passed_user(
        update: Update,
        context: CallbackContext,
        new_version: bool = False,
) -> None | int | SharedUser:
    if new_version:
        result = await custom_request_user(app=context.application, message=update.message, )
    else:
        result = await custom_accept_user(app=context.application, message=update.message, )
        if result is None:  # Only accept_user can return incorrect_user
            await context.view.warn.incorrect_user()
    return result


async def check_is_collections_chosen(context: CallbackContext, ) -> bool:
    if not context.user_data.tmp_data.collections_to_share.ids:
        await context.view.collections.collections_to_share_not_chosen(
            reply_to_message_id=context.user_data.tmp_data.collections_to_share.message_id_with_collections
        )
        return False
    return True


async def callback_to_post(
        update: Update,
        context: CallbackContext,
) -> ChannelPublicPost | BotPublicPost | PersonalPost | None:
    # Delete post / post buttons on error?
    # Dirty, better to bind cbk and cls
    if update.callback_query.data.startswith(VoteCbks.CHANNEL_PUBLIC_VOTE):
        post_cls = ChannelPublicPost
    elif update.callback_query.data.startswith(VoteCbks.PUBLIC_VOTE):
        post_cls = BotPublicPost  # BotPublicPost or PublicPost
    elif update.callback_query.data.startswith(VoteCbks.PERSONAL_VOTE):
        post_cls = PersonalPost
    else:
        raise UnknownPostType

    post = post_cls.from_callback(callback=update.callback_query, connection=context.connection, )
    if post is None:
        await context.view.posts.post_to_vote_not_found(tooltip=update.callback_query, )
        known_exceptions_logger.info(
            msg=f'{PostNotFound(post=post, )} - cbk_data: {update.callback_query.data}',
            exc_info=True,
        )
    return post
