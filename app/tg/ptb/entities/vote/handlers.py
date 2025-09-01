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


from app.postconfig import app_logger
from app.entities.shared.exceptions import UnknownPostType

from app.tg.ptb.actions import callback_to_post as actions_callback_to_post
from .model import PublicVote, PersonalVote
from . import texts

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext
    from rubik_core.entities.vote.model import HandledVote


def get_answer_text(handled_vote: HandledVote, ) -> str:
    if handled_vote.is_accepted is True:
        match handled_vote.new_value:
            case PublicVote.Value.POSITIVE:
                return texts.SUCCESS_VOTE_POSITIVE
            case PublicVote.Value.NEGATIVE:
                return texts.SUCCESS_VOTE_NEGATIVE
            case PublicVote.Value.ZERO:
                return texts.SUCCESS_VOTE_ZERO
    elif handled_vote.is_accepted is False:
        if handled_vote.new_value.value >= PublicVote.Value.POSITIVE:
            return texts.VOTE_ALREADY_SET_POSITIVE
        if handled_vote.new_value.value <= PublicVote.Value.NEGATIVE:
            return texts.VOTE_ALREADY_SET_NEGATIVE


async def public_vote_cbk_handler(update: Update, context: CallbackContext, ):
    """
    Callback may be abused, remember this!
    If user pressed button from forwarded message (default disable):
    https://stackoverflow.com/q/46756643/11277611
    """
    try:
        post = await actions_callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, UnknownPostType,) as e:
        app_logger.error(msg=e, exc_info=True, )
        await context.view.posts.voting_internal_error(tooltip=update.callback_query, )
        return
    else:  # If no exception was raised
        vote = PublicVote.from_callback(
            user=context.user,
            callback=update.callback_query,
        )
        handled_vote = context.user.set_vote(post=post, vote=vote, )
        if handled_vote.is_accepted:
            """Counting votes in keyboard was disabled (tmp or persistence)"""
            # Update public votes
            # context.dispatcher.run_async(func=services.System.BotPublicPost.mass_update_keyboard_job, bot_post=post, )
            await context.view.posts.bot_public_post.update_poll_keyboard(
                post=post,
                clicker_vote=vote,
                keyboard=update.effective_message.reply_markup,
            )
        await update.callback_query.answer(text=get_answer_text(handled_vote=handled_vote, ), )


async def channel_public_vote_cbk_handler(update: Update, context: CallbackContext, ):
    """
    Callback may be abused, remember this!
    If user pressed button from forwarded message (default disable):
    https://stackoverflow.com/q/46756643/11277611
    """
    vote = PublicVote.from_callback(user=context.user, callback=update.callback_query, )
    try:
        post = await actions_callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, UnknownPostType,) as e:
        app_logger.error(msg=e, exc_info=True, )
        await context.view.posts.voting_internal_error(tooltip=update.callback_query, )
    else:  # If no exception was raised
        handled_vote = context.user.set_vote(post=post, vote=vote, )
        if handled_vote.is_accepted is True:
            await context.view.posts.channel_public_post.update_poll_keyboard(
                post=post,
                # Regular post.message_id - is store channel message_id
                message_id=update.callback_query.message.message_id,
            )
        await update.callback_query.answer(text=get_answer_text(handled_vote=handled_vote, ), )


async def personal_vote_cbk_handler(update: Update, context: CallbackContext, ):
    _, str_opposite_id, post_id = update.callback_query.data.split()
    try:
        # TODO add method to get 2 voted users at the same time
        post = await actions_callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, UnknownPostType,) as e:
        app_logger.error(msg=e, exc_info=True, )
        await context.view.posts.voting_internal_error(tooltip=update.callback_query, )
        return
    else:  # If no exception
        clicker_vote = PersonalVote.from_callback(user=context.user, callback=update.callback_query, )
        handled_vote = context.user.set_vote(post=post, vote=clicker_vote, )
        if handled_vote.is_accepted:
            opposite_vote = None
            if int(str_opposite_id) != context.user.id:  # If Shown to myself
                opposite_vote = PersonalVote.get_user_vote(
                    user=PersonalVote.User(id=int(str_opposite_id), connection=context.connection, ),
                    post=post,
                )
            await context.view.posts.personal.update_poll_keyboard(
                post=post,
                clicker_vote=clicker_vote,
                opposite_vote=opposite_vote,
                keyboard=update.effective_message.reply_markup,
            )
        await update.callback_query.answer(text=get_answer_text(handled_vote=handled_vote, ), )
