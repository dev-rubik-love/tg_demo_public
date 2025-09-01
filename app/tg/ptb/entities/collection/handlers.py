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

from telegram.error import TelegramError

from ..shared.texts import Words as SharedWords
from .model import Collection
from .view import Keyboards as ViewKeyboards
from .services import Collection as CollectionService
from .texts import Collections as Texts
from ..post.model import VotedPost
from app.tg.ptb import custom
from app.tg.ptb.actions import extract_passed_user

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


async def get_my_collections_handler_cmd(_: Update, context: CallbackContext, ):
    """Return keyboard with personal collection names"""
    if collections := context.user.get_collections():
        await context.view.collections.show_my_collections(collections=collections, )
    else:
        await context.view.collections.no_collections()


class SharePersonalCollections:

    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        # User personal collections may be cached
        if collections := context.user.get_collections(cache=True, ):
            sent_message = await context.view.collections.show_collections(
                collections=collections,
                text=Texts.ASK_TO_SHARE,
                keyboard=ViewKeyboards.Inline.Mark,
            )
            context.user_data.tmp_data.collections_to_share = context.user_data.tmp_data.CollectionsToShare(
                message_id_with_collections=sent_message.message_id,
            )
            await context.view.notify_ready_keyword()
            return 0
        else:
            await context.view.collections.no_collections()
            return custom.end_conversation()

    @staticmethod
    async def mark_to_share_cbk_handler(update: Update, context: CallbackContext, ):
        """Mark collections to be shared"""
        # TODO mark selected posts
        collection_id = ViewKeyboards.Inline.Mark.extract_cbk_data(cbk_data=update.callback_query.data, )
        if collection_id in context.user_data.tmp_data.collections_to_share.ids:
            context.user_data.tmp_data.collections_to_share.ids.remove(collection_id)
            await update.callback_query.answer(text=Texts.COLLECTION_SUCCESS_REMOVED)  # TODO use chose keyboard
        else:
            context.user_data.tmp_data.collections_to_share.ids.add(collection_id)
            await update.callback_query.answer(text=Texts.COLLECTION_SUCCESS_ADDED)  # TODO use chose keyboard

    @staticmethod
    async def continue_handler(update: Update, context: CallbackContext, ):
        """Check is user finished to choose collections to share"""
        if update.message.text.lower().strip() != SharedWords.FINISH.lower():
            await context.view.warn.incorrect_finish()
            return
        if not context.user_data.tmp_data.collections_to_share.ids:
            await context.view.collections.collections_to_share_not_chosen(
                reply_to_message_id=context.user_data.tmp_data.collections_to_share.message_id_with_collections
            )
            return
        await context.view.collections.ask_who_to_share()
        return 1

    @staticmethod
    async def recipient_handler(update: Update, context: CallbackContext, ):
        """Get correct recipient from user"""
        shared_recipient = await extract_passed_user(update=update, context=context, new_version=True, )
        if not shared_recipient:
            await context.view.user_not_found()
            return
        try:
            await context.view.collections.ask_accept_collections(
                recipient_id=shared_recipient.user_id,
                collections_ids=context.user_data.tmp_data.collections_to_share.ids,
            )
        except TelegramError:  # If suddenly deleted
            await context.view.user_not_found()
            return
        await context.view.say_user_got_share_proposal(shared_recipient=shared_recipient, )
        context.user_data.tmp_data.collections_to_share = None
        return custom.end_conversation()

    @staticmethod
    async def recipient_decision_cbk_handler(update: Update, context: CallbackContext, ):
        """
        cbk handling accessible anytime
        - - -
        Not a part of this CH but logically related.
        A small difference with app.tg.ptb.handlers.start.accept_collections_cbk_handler
        because here (logically) only sender collections (for now), there any collections (including defaults).
        """
        try:
            _, str_sender_id, str_flag, *str_collections_id = update.callback_query.data.split()
            if bool(int(str_flag)) is False:  # If declined
                await context.view.collections.recipient_declined_share_proposal(
                    sender_id=int(str_sender_id),
                )
                return
            # Got collections ids may contain not only sender collections but a default too
            collections = CollectionService.get_by_ids(
                ids=[int(str_collection_id) for str_collection_id in str_collections_id],
                user=context.user,
            )
            if not collections:
                await context.view.collections.shared_collections_not_found()
                return
            await context.view.collections.show_shared_collections(
                sender_id=int(str_sender_id),
                collections=collections,  # Create user.read_marked_collections method?
            )
            await context.view.collections.recipient_accepted_share_proposal(
                sender_id=int(str_sender_id),  # Need name rather than id, but ok
            )
            await context.view.posts.use_get_stats_with_cmd(id=int(str_sender_id), )
            await context.view.posts.use_get_stats_with_cmd(id=context.user.id, )
        finally:
            await context.view.posts.remove_sharing_message(message=update.effective_message, )
            await update.callback_query.answer()

    @staticmethod
    async def show_collection_posts_to_recipient_cbk_handler(update: Update, context: CallbackContext, ):
        """cbk handling accessible anytime. Not a part of this CH but logically related (?)."""
        sender, collection_id = ViewKeyboards.Inline.ShowPostsToRecipient.extract_cbk_data(
            cbk_data=update.callback_query.data,
            user=context.user,
        )
        posts = Collection.get_posts(collection_id=collection_id, connection=context.connection, )
        voted_posts = VotedPost.from_posts(posts=posts, clicker=context.user, opposite=sender, )
        await context.view.collections.show_collection_posts(posts=voted_posts, tooltip=update.callback_query, )
        await update.callback_query.answer()


async def show_collection_posts_cbk_handler(update: Update, context: CallbackContext, ):
    """Show posts of the collection. cbk handling accessible anytime."""

    collection_id = ViewKeyboards.Inline.ShowCollections.extract_cbk_data(
        cbk_data=update.callback_query.data,
    )
    collection_posts = Collection.get_posts(collection_id=collection_id, connection=context.connection, )
    collection_posts = VotedPost.from_posts(posts=collection_posts, clicker=context.user, )
    await context.view.collections.show_collection_posts(posts=collection_posts, tooltip=update.callback_query, )
    await update.callback_query.answer()
