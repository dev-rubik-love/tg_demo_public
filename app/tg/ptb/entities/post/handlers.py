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
from typing import TYPE_CHECKING, Type
from dataclasses import dataclass

from telegram.error import TelegramError
from app.postconfig import app_logger

from . import model, constants
from .forms import Public as PublicPostForm, Personal as PersonalPostForm

from app.tg.ptb.custom import (
    end_conversation as utils_end_conversation,
    request_user as custom_request_user,
)
from app.tg.ptb.actions import extract_passed_user
from ..mix.services import System as SystemService
from ..collection.view import Keyboards as CollectionViewKeyboards
from ..shared.texts import Words as SharedWords

from app.tg.ptb.inline_mode import add_post_to_inline_data

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


class CreatePublicPost:

    SEND_KEYWORD = SharedWords.SEND.lower()

    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        await context.view.posts.say_public_post_hello()
        return 0

    @staticmethod
    async def sample_handler(update: Update, context: CallbackContext, ):
        """
        telegram has bot.send_media_group method to send message with multiple attachments,
        but documents and audios can't be mixed with another type of attachments.
        So I'm just sending multiple messages one by one.
        """
        context.user_data.forms.public_post = PublicPostForm(
            author=context.user,
            channel_id=update.effective_chat.id,
            message_id=update.message.message_id,
            message=update.effective_message,
        )
        await context.view.posts.here_post_preview()
        await context.view.posts.show_form(form=context.user_data.forms.public_post, )
        return 1

    @classmethod
    async def confirm_handler(cls, update: Update, context: CallbackContext, ):
        if update.message.text.lower().strip() == cls.SEND_KEYWORD.lower():
            stored_message_id_obj = await context.view.posts.store_in_channel(
                message_id=context.user_data.forms.public_post.message_id,
            )
            context.user_data.forms.public_post.message_id = stored_message_id_obj.message_id
            created_post = context.user_data.forms.public_post.create()
            await context.view.posts.say_success_post()
            add_post_to_inline_data(inline_data=context.bot_data.inline_data, post=created_post, )
        else:
            await context.view.warn.incorrect_send()
            return
        # Quickfix to create public votes for bots
        try:
            SystemService.set_bots_votes_to_post(post=created_post, )
        except Exception as e:
            app_logger.error(msg=e, exc_info=True, )
        context.user_data.forms.public_post = None  # Clear to spare space
        return utils_end_conversation()


class CreatePersonalPost:

    SEND_KEYWORD = SharedWords.SEND.capitalize()
    SKIP_KEYWORD = SharedWords.SKIP.capitalize()
    FINISH_KEYWORD = SharedWords.FINISH.capitalize()
    READY_R = constants.Regex.READY_R

    @dataclass
    class Keyboards:
        ChooseForPost: Type[CollectionViewKeyboards.Inline.ChooseForPost] = CollectionViewKeyboards.Inline.ChooseForPost

    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        await context.view.posts.say_personal_post_hello()
        return 0

    @classmethod
    async def entry_point_handler(cls, update: Update, context: CallbackContext, ):
        context.user_data.forms.personal_post = PersonalPostForm(
            author=context.user,
            channel_id=update.effective_chat.id,
            message_id=update.message.message_id,
        )
        await context.view.posts.here_post_preview()
        await context.view.posts.show_form(form=context.user_data.forms.personal_post, )
        await context.view.notify_ready_keyword(keyword=cls.SEND_KEYWORD, )
        return 1

    @classmethod
    async def post_sample_handler(cls, update: Update, context: CallbackContext, ):
        if update.message.text.strip().capitalize() != cls.SEND_KEYWORD:
            await context.view.warn.incorrect_continue(keyword=cls.SEND_KEYWORD, )
            return
        collections = context.user.get_collections(cache=True, )
        if collections:
            collection_names_from_db = {collection.name for collection in collections}
            # If user aware about collections (has it) - use them, else - default
            context.user_data.forms.personal_post.user_collections_count = len(collection_names_from_db)
        # Set the same keyboard for every collection (should be moved to view?)
        # ask_collections_for_post and show_collections should be moved to posts view and merged into single method,
        # but it's a bit hard cuz posts view depends on the collections view and vice versa
        await context.view.collections.propose_collections_for_post(collections=collections, )
        return 2

    @classmethod
    async def collection_name_cbk_handler(cls, update: Update, context: CallbackContext, ):
        collection_name, is_chosen = cls.Keyboards.ChooseForPost.extract_cbk_data(
            cbk_data=update.callback_query.data,
        )
        context.user_data.forms.personal_post.handle_collection_name_btn(
            collection_name=collection_name,
            is_chosen=is_chosen,  # Don't forget to swap, by default collection coming unchecked
        )
        await context.view.collections.update_chosen_collection(
            collection_name=collection_name,
            is_chosen=is_chosen,
            tooltip=update.callback_query,
            keyboard=cls.Keyboards.ChooseForPost.update_keyboard(
                btn_cbk_data=update.callback_query.data,
                # TODO keyboard need to replicate it cuz building a new one a bit hard cuz was placed in services
                keyboard=update.effective_message.reply_markup,
            ),
        )
        return 2

    @classmethod
    async def collection_names_text_handler(cls, update: Update, context: CallbackContext, ):
        text = update.effective_message.text.strip()
        context.user_data.forms.personal_post.handle_collection_names(text=text, )
        if context.user_data.forms.personal_post.collection_names:
            await context.view.collections.show_chosen_collections_for_post(
                collection_names=context.user_data.forms.personal_post.collection_names,
            )
        return None

    @classmethod
    async def confirm_handler(cls, _: Update, context: CallbackContext, ):
        stored_message_id_obj = await context.view.posts.store_in_channel(
            message_id=context.user_data.forms.personal_post.message_id,
        )
        context.user_data.forms.personal_post.message_id = stored_message_id_obj.message_id
        context.user_data.forms.personal_post.create()
        await context.view.posts.say_success_post()
        context.user_data.forms.personal_post = None  # Clear to spare space
        return utils_end_conversation()


async def update_public_post_status_cbk(update: Update, context: CallbackContext, ):
    _, str_post_id, str_new_status = update.callback_query.data.split()
    post = model.PublicPost.read(post_id=int(str_post_id), connection=context.connection, )
    post.update_status(status=post.Status(int(str_new_status)))
    await context.view.say_ok()
    return await update.callback_query.answer()


async def get_public_post(_: Update, context: CallbackContext, ):
    # TODO Put user in queue if not posts; Save in cache is mass posts exists
    if public_post := context.user.get_new_public_post():
        old_vote = context.user.get_vote(post=public_post, )
        await context.view.posts.delete_post(message_id=old_vote.message_id, )  # Delete old post
        sent_message = await context.view.posts.show_post(post=public_post, )
        context.user.upsert_shown_post(message_id=sent_message.message_id, public_post=public_post, )
    elif context.user.matcher.is_user_has_covotes:  # Behavior
        await context.view.posts.no_new_posts()  # No new posts for user
    else:
        await context.view.posts.no_mass_posts()


async def get_my_personal_posts(_: Update, context: CallbackContext, ):
    if personal_posts := context.user.get_personal_posts():
        voted_posts = model.VotedPersonalPost.from_posts(
            posts=personal_posts,
            clicker=context.user,
            opposite=context.user,
        )
        await context.view.posts.here_your_personal_posts()
        await context.view.posts.show_posts(posts=voted_posts)
    else:
        await context.view.posts.no_personal_posts()


class SharePersonalPosts:
    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        # User personal posts may be cached
        if context.user.get_personal_posts():
            await context.view.posts.ask_who_to_share_personal_posts()
            return 0
        else:
            await context.view.posts.no_personal_posts()
            return utils_end_conversation()

    @staticmethod
    async def recipient_handler(update: Update, context: CallbackContext, ):
        shared_recipient = await custom_request_user(app=context.application, message=update.effective_message, )
        if not shared_recipient:
            await context.view.warn.incorrect_user()
            return
        try:
            await context.view.posts.ask_accept_personal_posts(
                recipient_id=shared_recipient.user_id,  # Used only as chat_id
            )
            await context.view.say_user_got_share_proposal(shared_recipient=shared_recipient, )
        except TelegramError:
            await context.view.user_not_found()
            return
        return utils_end_conversation()

    @staticmethod
    async def recipient_decision_cbk_handler(update: Update, context: CallbackContext, ):
        try:
            posts_sender, flag = model.PersonalPost.extract_cbk_data(callback_data=update.callback_query.data, )
            if flag:
                await context.view.posts.user_accepted_share_proposal(
                    accepter_username=context.user.ptb.name,
                    posts_sender_id=posts_sender.id,
                )
                await context.view.posts.share_posts(
                    sender=posts_sender,
                    recipient=context.user,
                )
                await context.view.posts.use_get_stats_with_cmd(id=posts_sender.id, )
                await context.view.posts.use_get_stats_with_cmd(id=context.user.id, )
            else:
                await context.view.posts.user_declined_share_proposal(
                    posts_sender_id=posts_sender.id,
                )
        finally:
            await context.view.posts.remove_sharing_message(message=update.effective_message, )
            await update.callback_query.answer()


class RequestPersonalPosts:
    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        await context.view.posts.ask_who_to_request_personal_posts()
        return 0

    @staticmethod
    async def recipient_handler(update: Update, context: CallbackContext, ):
        shared_recipient = await extract_passed_user(update=update, context=context, new_version=True, )
        if shared_recipient:
            try:
                await context.view.posts.ask_permission_to_share_personal_posts(
                    recipient_id=shared_recipient.user_id,
                )
                await context.view.say_user_got_request_proposal(shared_recipient=shared_recipient, )
            except TelegramError:
                await context.view.user_not_found()
                return
        return utils_end_conversation()

    @staticmethod
    async def recipient_decision_cbk_handler(update: Update, context: CallbackContext, ):
        try:
            posts_recipient, flag = model.PersonalPost.extract_cbk_data(
                callback_data=update.callback_query.data,
            )
            if not flag:
                await context.view.posts.user_declined_request_proposal(
                    posts_recipient_id=posts_recipient.id,
                )
                return
            await context.view.posts.user_accepted_request_proposal(
                posts_recipient_id=posts_recipient.id,
            )
            is_shared_success = await context.view.posts.share_posts(
                sender=context.user,
                recipient=posts_recipient,
            )
            if is_shared_success is False:
                await context.view.posts.no_personal_posts()  # Notify user itself
                await context.view.posts.sender_has_no_personal_posts(
                    recipient_id=posts_recipient.id,
                )
            else:
                await context.view.posts.use_get_stats_with_cmd(id=posts_recipient.id, )
                await context.view.posts.use_get_stats_with_cmd()
        finally:
            await context.view.posts.remove_sharing_message(message=update.effective_message, )
            await update.callback_query.answer()
