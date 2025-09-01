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
from typing import TYPE_CHECKING, Iterable

from telegram.error import TelegramError
from telegram import ReplyKeyboardMarkup as tg_RKM, InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

from app.postconfig import known_exceptions_logger
from app.entities.shared.exceptions import PostNotFound

from .constants import Cmds, Cbks, PostsChannels
from . import forms, model
from .texts import Posts as Texts
from ..shared.view import SharedInit, Shared, Keyboards as SharedKeyboards
from ..texts import USE_GET_STATS_WITH_CMD
from ..vote.constants import Cbks as VoteCbks

if TYPE_CHECKING:
    from telegram import Message, MessageId, CallbackQuery
    from ..vote.model import IPublicVote, IPersonalVote
    from ..user.model import IUser


class Public(SharedInit):

    class Shared:

        MARK_VOTE = '🔹'
        POS_EMOJI = '👍'
        NEG_EMOJI = '👎'
        LIKE_TEXT = POS_EMOJI  # Used also in form
        DISLIKE_TEXT = NEG_EMOJI  # Used also in form

        @classmethod
        def get_keyboard(cls, post_id: int, clicker_vote: IPublicVote, pattern: str, ) -> tg_IKM:

            pos_btn_text = cls.LIKE_TEXT
            neg_btn_text = cls.DISLIKE_TEXT
            if clicker_vote.value == clicker_vote.Value.POSITIVE:
                pos_btn_text = f'{cls.POS_EMOJI}{cls.MARK_VOTE}'
            elif clicker_vote.value == clicker_vote.Value.NEGATIVE:
                neg_btn_text = f'{cls.NEG_EMOJI}{cls.MARK_VOTE}'

            return tg_IKM.from_row(
                button_row=(
                    tg_IKB(
                        text=neg_btn_text,
                        callback_data=f'{pattern} {clicker_vote.user.id} -{post_id}',
                    ),
                    tg_IKB(
                        text=pos_btn_text,
                        callback_data=f'{pattern} {clicker_vote.user.id} +{post_id}',
                    ),), )

    @classmethod
    def get_keyboard(cls, post: model.IPublicPost, clicker_vote: IPublicVote, ) -> tg_IKM:
        return cls.Shared.get_keyboard(
            post_id=post.id,
            clicker_vote=clicker_vote,
            pattern=VoteCbks.PUBLIC_VOTE,
        )

    async def show(self, post: model.IPublicPost, clicker_vote: IPublicVote, ) -> MessageId:
        return await self.bot.copy_message(
            chat_id=clicker_vote.user.id,
            from_chat_id=PostsChannels.STORE.value,
            message_id=post.message_id,
            reply_markup=self.get_keyboard(post=post, clicker_vote=clicker_vote, ),
        )


class BotPublicPost(SharedInit, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""

    MARK_VOTE = '🔹'
    POS_EMOJI = '👍'
    NEG_EMOJI = '👎'
    CBK_PREFIX = VoteCbks.PUBLIC_VOTE

    @classmethod
    def get_keyboard(cls, post: model.IBotPublicPost, clicker_vote: IPublicVote, ) -> tg_IKM:
        return Public.Shared.get_keyboard(  # TODO
            post_id=post.id,
            clicker_vote=clicker_vote,
            pattern=cls.CBK_PREFIX,
        )

    async def update_poll_keyboard(
            self,
            post: model.IBotPublicPost,
            clicker_vote: IPublicVote,
            keyboard: tg_IKM,
    ) -> Message:
        if SharedKeyboards.check_is_close_btn(btn=keyboard.inline_keyboard[-1][-1]):
            new_keyboard = SharedKeyboards.add_btn(
                keyboard=self.get_keyboard(post=post, clicker_vote=clicker_vote, ),
                btn=keyboard.inline_keyboard[-1][-1],
            )
        else:
            new_keyboard = self.get_keyboard(post=post, clicker_vote=clicker_vote, )
        return await self.bot.edit_message_reply_markup(
            chat_id=clicker_vote.user.id,
            message_id=clicker_vote.message_id,
            reply_markup=new_keyboard,
        )


class ChannelPublicPost(SharedInit, ):

    MARK_VOTE = '🔹'
    POS_EMOJI = '👍'
    NEG_EMOJI = '👎'
    CBK_PREFIX = VoteCbks.CHANNEL_PUBLIC_VOTE

    @classmethod
    def get_keyboard(cls, post: model.IChannelPublicPost, ) -> tg_IKM:
        """keyboard without mark symbol"""
        return tg_IKM.from_row(
            button_row=(
                tg_IKB(
                    text=f'{cls.NEG_EMOJI} {post.dislikes_count}',
                    callback_data=f'{cls.CBK_PREFIX} -{post.id}',
                ),
                tg_IKB(
                    text=f'{cls.POS_EMOJI} {post.likes_count}',
                    callback_data=f'{cls.CBK_PREFIX} +{post.id}',
                ),), )

    async def update_poll_keyboard(self, post: model.IChannelPublicPost, message_id: int, ) -> Message:
        return await self.bot.edit_message_reply_markup(
            chat_id=PostsChannels.POSTS.value,
            message_id=message_id,  # just post.message_id - is store channel message_id
            reply_markup=self.get_keyboard(post=post, ),
        )

    async def show(
            self,
            post: model.IChannelPublicPost,
            source_chat_id: int = PostsChannels.STORE.value,
            target_chat_id: int = PostsChannels.STORE.value,
    ) -> MessageId:
        """show the same as send (send reviewed and deprecated) """
        sent_message = await self.bot.copy_message(
            chat_id=target_chat_id,
            from_chat_id=source_chat_id,
            message_id=post.message_id,
            reply_markup=self.get_keyboard(post=post, ),
        )
        return sent_message


class Personal(SharedInit):

    class Shared:
        MARK_VOTE = '🔹'
        NEG_EMOJI = '👎'
        POS_EMOJI = '❤'
        LIKE_TEXT = 'like'
        DISLIKE_TEXT = 'dislike'

    @classmethod
    def get_keyboard(
            cls,
            post: model.IPersonalPost,
            clicker_vote: IPersonalVote,
            opposite_vote: IPersonalVote | None = None,
    ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite id (clicker accessible from update)
        """

        if clicker_vote.value == clicker_vote.Value.POSITIVE:
            pos_btn_text = f'{cls.Shared.POS_EMOJI}{cls.Shared.MARK_VOTE}'
            neg_btn_text = ''
        elif clicker_vote.value == clicker_vote.Value.NEGATIVE:
            neg_btn_text = f'{cls.Shared.NEG_EMOJI}{cls.Shared.MARK_VOTE}'
            pos_btn_text = ''
        else:
            pos_btn_text = neg_btn_text = ''

        if opposite_vote is not None:
            opposite_user_id = opposite_vote.user.id  # int or str no matter here
            if opposite_vote.value == clicker_vote.Value.POSITIVE:
                pos_btn_text = f'{pos_btn_text}{cls.Shared.POS_EMOJI}'
            elif opposite_vote.value == clicker_vote.Value.NEGATIVE:
                neg_btn_text = f'{neg_btn_text}{cls.Shared.NEG_EMOJI}'
        else:
            opposite_user_id = clicker_vote.user.id  # Just my id twice, it's easiest to parse in handlers

        cbk = f'{VoteCbks.PERSONAL_VOTE} {opposite_user_id} {{}}{post.id}'  # {{}} - for next format method
        return tg_IKM.from_row(
            button_row=(
                tg_IKB(text=neg_btn_text or cls.Shared.DISLIKE_TEXT, callback_data=cbk.format('-')),
                tg_IKB(text=pos_btn_text or cls.Shared.LIKE_TEXT, callback_data=cbk.format('+')),
            ), )

    async def update_poll_keyboard(
            self,
            post: model.IPersonalPost,
            clicker_vote: IPersonalVote,
            opposite_vote: IPersonalVote,
            keyboard: tg_IKM,
    ) -> Message | bool:
        if SharedKeyboards.check_is_close_btn(btn=keyboard.inline_keyboard[-1][-1]):
            new_keyboard = SharedKeyboards.add_btn(
                keyboard=self.get_keyboard(post=post, clicker_vote=clicker_vote, opposite_vote=opposite_vote, ),
                btn=keyboard.inline_keyboard[-1][-1],
            )
        else:
            new_keyboard = self.get_keyboard(
                post=post,
                clicker_vote=clicker_vote,
                opposite_vote=opposite_vote,
            )
        return await self.bot.edit_message_reply_markup(
            chat_id=clicker_vote.user.id,
            message_id=clicker_vote.message_id,
            reply_markup=new_keyboard,
        )

    async def show(
            self,
            post: model.IPersonalPost,
            clicker_vote: IPersonalVote,
            opposite_vote: IPersonalVote | None = None,
    ):
        return await self.bot.copy_message(
            chat_id=clicker_vote.user.id,
            from_chat_id=PostsChannels.STORE.value,
            message_id=post.message_id,
            reply_markup=self.get_keyboard(
                post=post,
                clicker_vote=clicker_vote,
                opposite_vote=opposite_vote,
            ), )


class BotPersonalPost(SharedInit, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""
    # TODO


class Posts(SharedInit):
    Public = Public
    BotPublicPost = BotPublicPost
    ChannelPublicPost = ChannelPublicPost
    Personal = Personal
    BotPersonalPost = BotPersonalPost

    def __init__(self, shared_view: Shared, user: IUser, ) -> None:
        super().__init__(user=user, )
        self.public = self.Public(user=user, )
        self.channel_public_post = self.ChannelPublicPost(user=user, )
        self.bot_public_post = self.BotPublicPost(user=user, )
        self.personal = self.Personal(user=user, )
        self.bot_personal_post = self.BotPersonalPost(user=user, )
        self.shared: Shared = shared_view

    remove_sharing_message = Shared.remove_sharing_message

    async def store_in_channel(self, message_id: int, ) -> MessageId:
        return await self.bot.copy_message(  # Try forward message rather than copy on fail
            chat_id=PostsChannels.STORE.value,
            from_chat_id=self.id,
            message_id=message_id,
        )

    async def delete_post(self, message_id: int, chat_id: int | None = None, ) -> bool:
        return await self.bot.delete_message(chat_id=chat_id or self.id, message_id=message_id, )

    async def no_mass_posts(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.Public.NO_MASS_POSTS, )

    async def show_pending(self, post: model.IPublicPost, ) -> MessageId:
        return await self.bot.copy_message(
            chat_id=self.id,
            from_chat_id=PostsChannels.STORE.value,
            message_id=post.message_id,
            reply_markup=Keyboards.ShowPending.update_status(post=post, )
        )

    async def no_new_posts(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.Public.NO_NEW_POSTS, )

    async def no_personal_posts(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.Personal.NO_POSTS,
            reply_markup=Keyboards.create_personal_post,
        )

    async def sender_has_no_personal_posts(self, recipient_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=recipient_id,
            text=Texts.Personal.SENDER_HAS_NO_POSTS,
        )

    async def user_declined_share_proposal(self, posts_sender_id: int, ) -> Message:
        return await self.shared.user_declined_share_proposal(
            id=posts_sender_id,
            decliner_username=self.user.ptb.name,
        )

    async def user_declined_request_proposal(self, posts_recipient_id: int, ) -> Message:
        return await self.shared.user_declined_request_proposal(
            id=posts_recipient_id,
            decliner_username=self.user.ptb.name,
        )

    async def user_accepted_share_proposal(self, accepter_username: str, posts_sender_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=posts_sender_id,
            text=Texts.Personal.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_USERNAME=accepter_username),
        )

    async def user_accepted_request_proposal(self, posts_recipient_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=posts_recipient_id,
            text=Texts.Personal.USER_ACCEPTED_REQUEST_PROPOSAL.format(ACCEPTER_USERNAME=self.user.ptb.name),
        )

    async def post_to_vote_not_found(self, tooltip: CallbackQuery, ) -> Message | bool:
        return await tooltip.answer(text=Texts.POST_TO_VOTE_NOT_FOUND, show_alert=True, )

    @staticmethod
    async def voting_internal_error(tooltip: CallbackQuery, ) -> Message | bool:
        """Vote itself has no view, cuz voting for user is only via (visible) post"""
        return await tooltip.answer(text=Texts.INTERNAL_ERROR, show_alert=True, )

    async def cant_send_posts_to_user_help_text(self, posts_recipient_id: int | None = None, ) -> Message:
        """  # Not in use"""
        return await self.bot.send_message(
            text=Texts.Personal.CANT_SEND_TO_THIS_USER,
            chat_id=posts_recipient_id or self.id
        )

    async def say_public_post_hello(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.Public.HELLO, )

    async def say_success_post(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.CREATED_SUCCESSFULLY, )

    async def say_personal_post_hello(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.Personal.HELLO,
            reply_markup=Keyboards.say_personal_post_hello,
        )

    async def ask_who_to_share_personal_posts(self, ):
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.Personal.WHO_TO_SHARE,
            reply_markup=Keyboards.request_chat(request_btn_params=dict(request_username=True, request_name=True, ), ),
        )

    async def ask_who_to_request_personal_posts(self, ):
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.Personal.WHO_TO_REQUEST,
            reply_markup=Keyboards.ask_who_to_request_personal_posts(),
        )

    async def ask_permission_to_share_personal_posts(self, recipient_id: int, ):
        return await self.bot.send_message(
            chat_id=recipient_id,
            text=Texts.Personal.NOTIFY_REQUEST_PROPOSAL.format(USERNAME=self.user.ptb.name),
            reply_markup=Keyboards.ask_permission_share_personal_post(id=self.id, ),
        )

    async def here_your_personal_posts(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.Personal.HERE_YOUR_POSTS, )

    async def ask_accept_personal_posts(self, recipient_id: int, ):
        """Proposal to share (send) a personal post to someone"""
        return await self.bot.send_message(
            chat_id=recipient_id,
            text=Texts.Personal.NOTIFY_SHARE_PROPOSAL.format(USERNAME=self.user.ptb.name),
            reply_markup=Keyboards.AcceptPosts.build(sender_id=self.id, ),
        )

    async def show_post(self, post: model.IVotedPublicPost | model.IVotedPersonalPost, ):
        if isinstance(post, model.VotedPublicPost, ):
            return await self.public.show(post=post.post, clicker_vote=post.clicker_vote, )
        else:
            return await self.personal.show(
                post=post.post,
                clicker_vote=post.clicker_vote,
                opposite_vote=post.opposite_vote,
            )

    async def show_posts(
            self,
            posts: list[model.IVotedPublicPost | model.IVotedPersonalPost,],
    ) -> list[Message]:
        sent_messages = []
        for post in posts:
            try:
                sent_messages.append(await self.show_post(post=post, ))
            except TelegramError:
                known_exceptions_logger.info(msg=PostNotFound(post=post, ), exc_info=True, )
        return sent_messages

    async def show_form(self, form: forms.Public | forms.Personal, ) -> MessageId:
        if isinstance(form, forms.Public, ):
            return await self.bot.copy_message(
                chat_id=form.author.id,
                from_chat_id=form.author.id,
                message_id=form.message_id,
                reply_markup=Keyboards.public_form,
            )
        else:
            return await self.bot.copy_message(
                chat_id=form.author.id,
                from_chat_id=form.author.id,
                message_id=form.message_id,
                reply_markup=Keyboards.personal_form,
            )

    async def share_post(
            self,
            post: model.IPersonalPost,
            post_sender: IUser,
            post_recipient: IUser,
    ) -> None:
        """Share post from one user to another (send the same post simultaneously to 2 users)"""
        post_sender_vote = post_sender.get_vote(post=post, )
        post_recipient_vote = post_recipient.get_vote(post=post, )
        await self.delete_post(chat_id=post_sender.id, message_id=post_sender_vote.message_id, )
        await self.delete_post(chat_id=post_recipient.id, message_id=post_sender_vote.message_id, )
        try:
            # send message to me
            sender_sent_message = await self.show_post(
                post=model.VotedPersonalPost(
                    post=post,
                    clicker_vote=post_sender_vote,
                    opposite_vote=post_recipient_vote,
                ),
            )
            # send message to opposite user
            recipient_sent_message = await self.show_post(
                post=model.VotedPersonalPost(
                    post=post,
                    clicker_vote=post_recipient_vote,
                    opposite_vote=post_sender_vote,
                ),
            )
        except TelegramError as e:
            known_exceptions_logger.error(msg=e, exc_info=True, )
            return None
        post_sender_vote.message_id = sender_sent_message.message_id
        post_recipient_vote.message_id = recipient_sent_message.message_id
        post_sender_vote.upsert_message_id()
        post_recipient_vote.upsert_message_id()

    async def share_posts(
            self,
            sender: IUser,
            recipient: IUser,
            posts: Iterable[model.IPersonalPost] | None = None,
    ) -> bool:
        posts = posts or sender.get_personal_posts()
        for post in posts:
            await self.share_post(post=post, post_sender=sender, post_recipient=recipient, )
        return bool(posts)

    async def here_post_preview(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=f'{Texts.HERE_POST_PREVIEW}',
            reply_markup=Keyboards.send_cancel,
        )

    async def use_get_stats_with_cmd(self, id: int | None = None, ) -> Message:
        return await self.bot.send_message(chat_id=id or self.id, text=USE_GET_STATS_WITH_CMD, )

    async def check_post_existence(self, post: model.IPublicPost | model.IPersonalPost, ) -> bool:
        return await self.shared.check_message_existence(
            chat_id=PostsChannels.STORE.value,
            message_id=post.message_id,
        )


class Keyboards:
    create_personal_post = tg_RKM(
        keyboard=[[Cmds.CREATE_PERSONAL_POST]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    send_cancel = SharedKeyboards.send_cancel
    say_personal_post_hello = SharedKeyboards.cancel
    ask_who_to_request_personal_posts = SharedKeyboards.request_user
    request_chat = SharedKeyboards.request_user

    public_form = tg_IKM.from_row(
        button_row=(
            tg_IKB(text=Posts.Public.Shared.DISLIKE_TEXT, callback_data=Cbks.EMPTY, ),
            tg_IKB(text=Posts.Public.Shared.LIKE_TEXT, callback_data=Cbks.EMPTY, ),
        ), )

    personal_form = tg_IKM.from_row(
        button_row=(
            tg_IKB(text=Posts.Personal.Shared.DISLIKE_TEXT, callback_data=Cbks.EMPTY, ),
            tg_IKB(text=Posts.Personal.Shared.LIKE_TEXT, callback_data=Cbks.EMPTY, ),
        ), )

    @staticmethod
    def ask_permission_share_personal_post(id: int, ) -> tg_IKM:
        return tg_IKM.from_row(
            button_row=(
                tg_IKB(
                    text=Texts.Personal.Buttons.DISALLOW,
                    callback_data=f'{Cbks.REQUEST_PERSONAL_POSTS} {id} 0'
                ),
                tg_IKB(
                    text=Texts.Personal.Buttons.ALLOW,
                    callback_data=f'{Cbks.REQUEST_PERSONAL_POSTS} {id} 1'
                ),
            ),
        )

    class ShowPending:
        BTN_1_TEXT = Texts.Public.Buttons.PENDING
        BTN_2_TEXT = Texts.Public.Buttons.READY_TO_RELEASE
        CBK_PREFIX = Cbks.UPDATE_PUBLIC_POST_STATUS

        @classmethod
        def build_cbk(cls, post_id: int, status: model.IPublicPost.Status, ):
            return f'{cls.CBK_PREFIX} {post_id} {status.value}'

        @classmethod
        def update_status(cls, post: model.IPublicPost, ) -> tg_IKM:
            return tg_IKM.from_row(
                button_row=(
                    tg_IKB(
                        text=cls.BTN_1_TEXT,
                        callback_data=cls.build_cbk(post_id=post.id, status=post.Status.PENDING, ),
                    ),
                    tg_IKB(
                        text=cls.BTN_2_TEXT,
                        callback_data=cls.build_cbk(post_id=post.id, status=post.Status.READY_TO_RELEASE, ),
                    ),), )

    class AcceptPosts:
        CBK_PREFIX = Cbks.ACCEPT_PERSONAL_POSTS
        DECLINE_TEXT = Texts.Personal.Buttons.DECLINE
        ACCEPT_TEXT = Texts.Personal.Buttons.ACCEPT

        @classmethod
        def build_cbk(cls, sender_id: int, flag: bool, ) -> str:
            return f'{cls.CBK_PREFIX} {sender_id} {int(flag)}'

        @classmethod
        def build(cls, sender_id: int, ) -> tg_IKM:
            return tg_IKM.from_row(
                button_row=(
                    tg_IKB(text=cls.DECLINE_TEXT, callback_data=cls.build_cbk(sender_id=sender_id, flag=False, ), ),
                    tg_IKB(text=cls.ACCEPT_TEXT, callback_data=cls.build_cbk(sender_id=sender_id, flag=True, ), ),
                ), )
