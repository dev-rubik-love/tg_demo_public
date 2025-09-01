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
from unittest.mock import call, ANY
from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from telegram.error import TelegramError
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

from rubik_core.entities.vote.base import Value as VoteValue

from app.tg.ptb.entities.post import view, model
from app.tg.ptb.entities.texts import USE_GET_STATS_WITH_CMD

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestBotPublicPost:

    @staticmethod
    def test_get_keyboard(
            bot_public_post_s: model.IBotPublicPost,
            public_vote_s: model.IPublicVote,
    ):
        result = view.BotPublicPost.get_keyboard(
            post=bot_public_post_s,
            clicker_vote=public_vote_s,
        )
        expected = view.Public.Shared.get_keyboard(
            post_id=bot_public_post_s.id,
            clicker_vote=public_vote_s,
            pattern=view.BotPublicPost.CBK_PREFIX,
        )
        assert result == expected

    @staticmethod
    @pytest.mark.parametrize(
        argnames='keyboard',
        argvalues=(
                tg_IKM.from_button(button=tg_IKB(text='1', callback_data='2', ), ),  # keyboard 1
                tg_IKM.from_button(  # keyboard 2
                    button=tg_IKB(
                        text=view.SharedKeyboards.HIDE_S,
                        callback_data=f'{view.SharedKeyboards.HIDE_S} 3',
                    ), ),
        ), )
    async def test_test_update_poll_keyboard(
            mock_view_f: MagicMock,
            bot_public_post_s: model.IBotPublicPost,
            public_vote_s: model.IPublicVote,
            keyboard: tg_IKM,
    ):
        result = await view.BotPublicPost.update_poll_keyboard(
            self=mock_view_f.posts.bot_public_post,
            post=bot_public_post_s,
            clicker_vote=public_vote_s,
            keyboard=keyboard,
        )
        mock_view_f.posts.bot_public_post.bot.edit_message_reply_markup.acow(
            chat_id=public_vote_s.user.id,
            message_id=public_vote_s.message_id,
            reply_markup=ANY,  # self.get_keyboard or shared keyboard `add_btn`
        )
        assert result == mock_view_f.posts.bot_public_post.bot.edit_message_reply_markup.return_value


class TestPublicPost:
    @staticmethod
    @pytest.mark.parametrize(argnames='value', argvalues=VoteValue, )
    def test_get_keyboard(
            public_post_s: model.IPublicPost,
            public_vote_s: model.IPublicVote,
            value: VoteValue,
            monkeypatch,
    ):
        monkeypatch.setattr(target=public_vote_s, name='value', value=value, )
        result = view.Posts.Public.get_keyboard(post=public_post_s, clicker_vote=public_vote_s, )
        expected = view.Public.Shared.get_keyboard(
            post_id=public_post_s.id,
            clicker_vote=public_vote_s,
            pattern=view.BotPublicPost.CBK_PREFIX,
        )
        assert result == expected

    @staticmethod
    async def test_show(
            mock_view_f: MagicMock,
            public_post_s: model.IPublicPost,
            public_vote_s: model.IPublicVote,
    ):
        result = await view.Posts.Public.show(
            self=mock_view_f.posts.public,
            post=public_post_s,
            clicker_vote=public_vote_s,
        )
        mock_view_f.posts.public.bot.copy_message.acow(
            chat_id=public_vote_s.user.id,
            from_chat_id=view.PostsChannels.STORE.value,
            message_id=public_post_s.message_id,
            reply_markup=mock_view_f.posts.public.get_keyboard.return_value,
        )
        mock_view_f.posts.public.get_keyboard.acow(post=public_post_s, clicker_vote=public_vote_s, )
        assert result == mock_view_f.posts.public.bot.copy_message.return_value

    class TestKeyboards:
        class TestShowPending:
            cls_to_test = view.Keyboards.ShowPending

            def test_build_cbk(self, mock_public_post: MagicMock, ):
                status = model.PublicPost.Status.PENDING  # Any status ok, just will be used ".value" attr
                result = self.cls_to_test.build_cbk(post_id=1, status=status, )
                assert result == f'{self.cls_to_test.CBK_PREFIX} 1 {status.value}'

            def test_update_status(self, public_post_s: model.IPublicPost, ):
                # Call ShowPending.update_status
                actual_keyboard = view.Keyboards.ShowPending.update_status(post=public_post_s, )
                expected_keyboard = tg_IKM.from_row(
                    button_row=(
                        tg_IKB(
                            text=self.cls_to_test.BTN_1_TEXT,
                            callback_data=self.cls_to_test.build_cbk(
                                post_id=public_post_s.id,
                                status=public_post_s.Status.PENDING,
                            )
                        ),
                        tg_IKB(
                            text=self.cls_to_test.BTN_2_TEXT,
                            callback_data=self.cls_to_test.build_cbk(
                                post_id=public_post_s.id,
                                status=public_post_s.Status.READY_TO_RELEASE,
                            )
                        ),), )
                assert actual_keyboard == expected_keyboard


class TestChannelPublicPost:
    """Test the ChannelPublicPost class."""

    @staticmethod
    def test_get_keyboard(channel_public_post_s: model.IChannelPublicPost, ):
        expected_keyboard = tg_IKM.from_row(
            button_row=(
                tg_IKB(
                    text=f'{view.ChannelPublicPost.NEG_EMOJI} {channel_public_post_s.dislikes_count}',
                    callback_data=f'{view.ChannelPublicPost.CBK_PREFIX} -{channel_public_post_s.id}',
                ),
                tg_IKB(
                    text=f'{view.ChannelPublicPost.POS_EMOJI} {channel_public_post_s.likes_count}',
                    callback_data=f'{view.ChannelPublicPost.CBK_PREFIX} +{channel_public_post_s.id}',
                ),), )
        actual_keyboard = view.ChannelPublicPost.get_keyboard(post=channel_public_post_s, )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    async def test_update_poll_keyboard(mock_view_f: MagicMock, channel_public_post_s: model.IChannelPublicPost, ):
        result = await view.ChannelPublicPost.update_poll_keyboard(
            self=mock_view_f.posts.channel_public_post,
            post=channel_public_post_s,
            message_id=1,
        )
        mock_view_f.posts.channel_public_post.bot.edit_message_reply_markup.acow(
            chat_id=view.PostsChannels.POSTS.value,
            message_id=1,
            reply_markup=mock_view_f.posts.channel_public_post.get_keyboard.return_value,
        )
        assert result == mock_view_f.posts.channel_public_post.bot.edit_message_reply_markup.return_value

    @staticmethod
    async def test_show(mock_view_f: MagicMock, channel_public_post_s: model.IChannelPublicPost, ):
        result = await view.ChannelPublicPost.show(
            self=mock_view_f.posts.channel_public_post,
            post=channel_public_post_s,
        )
        mock_view_f.posts.channel_public_post.bot.copy_message.acow(
            chat_id=view.PostsChannels.STORE.value,
            from_chat_id=view.PostsChannels.STORE.value,
            message_id=channel_public_post_s.message_id,
            reply_markup=mock_view_f.posts.channel_public_post.get_keyboard.return_value,
        )
        assert result == mock_view_f.posts.channel_public_post.bot.copy_message.return_value


class TestPersonalPost:

    class TestGetKeyboard:
        """test_get_keyboard"""

        @staticmethod
        @pytest.mark.parametrize(
            argnames='pos_btn_text, neg_btn_text, vote_value',
            argvalues=(
                    (
                            # Negative vote
                            view.Posts.Personal.Shared.LIKE_TEXT,
                            f'{view.Posts.Personal.Shared.NEG_EMOJI}'
                            f'{view.Posts.Personal.Shared.MARK_VOTE}'
                            f'{view.Posts.Personal.Shared.NEG_EMOJI}',
                            model.PersonalPost.Vote.Value.NEGATIVE,
                    ),
                    (
                            # Zero vote
                            view.Posts.Personal.Shared.LIKE_TEXT,
                            view.Posts.Personal.Shared.DISLIKE_TEXT,
                            model.PersonalPost.Vote.Value.ZERO,
                    ),
                    (
                            # Positive vote
                            f'{view.Posts.Personal.Shared.POS_EMOJI}'
                            f'{view.Posts.Personal.Shared.MARK_VOTE}'
                            f'{view.Posts.Personal.Shared.POS_EMOJI}',
                            view.Posts.Personal.Shared.DISLIKE_TEXT,
                            model.PersonalPost.Vote.Value.POSITIVE,

                    )
            ), )
        def test_opposite_vote_passed(  # TODO improve by bind vote value and text in architecture
                personal_post_s: model.IPersonalPost,
                personal_vote_s: model.IPersonalVote,
                vote_value: model.PersonalPost.Vote.Value,
                pos_btn_text: str,
                neg_btn_text: str,
                monkeypatch,
        ):
            opposite_vote = personal_vote_s
            cbk = f'{view.VoteCbks.PERSONAL_VOTE} {opposite_vote.user.id} {{}}{personal_post_s.id}'
            monkeypatch.setattr(personal_vote_s, 'value', vote_value, )
            expected_keyboard = tg_IKM.from_row(
                button_row=(
                    tg_IKB(text=neg_btn_text, callback_data=cbk.format('-'), ),
                    tg_IKB(text=pos_btn_text, callback_data=cbk.format('+'), ),
                ), )
            actual_keyboard = view.Posts.Personal.get_keyboard(
                post=personal_post_s,
                clicker_vote=personal_vote_s,
                opposite_vote=opposite_vote,
            )
            assert actual_keyboard == expected_keyboard

        @staticmethod
        @pytest.mark.parametrize(
            argnames='pos_btn_text, neg_btn_text, vote_value',
            argvalues=(
                    (
                            # Negative vote
                            view.Posts.Personal.Shared.LIKE_TEXT,
                            f'{view.Posts.Personal.Shared.NEG_EMOJI}'
                            f'{view.Posts.Personal.Shared.MARK_VOTE}',
                            model.PersonalPost.Vote.Value.NEGATIVE,
                    ),
                    (
                            # Zero vote
                            view.Posts.Personal.Shared.LIKE_TEXT,
                            view.Posts.Personal.Shared.DISLIKE_TEXT,
                            model.PersonalPost.Vote.Value.ZERO,
                    ),
                    (
                            # Positive vote
                            f'{view.Posts.Personal.Shared.POS_EMOJI}'
                            f'{view.Posts.Personal.Shared.MARK_VOTE}',
                            view.Posts.Personal.Shared.DISLIKE_TEXT,
                            model.PersonalPost.Vote.Value.POSITIVE,

                    )
            ), )
        def test_opposite_vote_not_passed(  # TODO improve by bind vote value and text in architecture
                personal_post_s: model.IPersonalPost,
                personal_vote_s: model.IPersonalVote,
                vote_value: model.PersonalPost.Vote.Value,
                pos_btn_text: str,
                neg_btn_text: str,
                monkeypatch,
        ):
            opposite_vote = None
            cbk = f'{view.VoteCbks.PERSONAL_VOTE} {personal_vote_s.user.id} {{}}{personal_post_s.id}'
            monkeypatch.setattr(personal_vote_s, 'value', vote_value, )
            expected_keyboard = tg_IKM.from_row(
                button_row=(
                    tg_IKB(text=neg_btn_text, callback_data=cbk.format('-'), ),
                    tg_IKB(text=pos_btn_text, callback_data=cbk.format('+'), ),
                ), )
            actual_keyboard = view.Posts.Personal.get_keyboard(
                post=personal_post_s,
                clicker_vote=personal_vote_s,
                opposite_vote=opposite_vote,
            )
            assert actual_keyboard == expected_keyboard

    @staticmethod
    @pytest.mark.parametrize(
        argnames='keyboard',
        argvalues=(
                tg_IKM.from_button(button=tg_IKB(text='1', callback_data='2', ), ),  # keyboard 1
                tg_IKM.from_button(  # keyboard 2
                    button=tg_IKB(
                        text=view.SharedKeyboards.HIDE_S,
                        callback_data=f'{view.SharedKeyboards.HIDE_S} 3',
                    ), ),
        ), )
    async def test_update_poll_keyboard(
            mock_view_f: MagicMock,
            mock_personal_post: MagicMock,
            personal_vote_s: model.IPersonalVote,
            keyboard: tg_IKM,
    ):
        result = await view.Posts.Personal.update_poll_keyboard(
            self=mock_view_f.posts.personal,
            post=mock_personal_post,
            clicker_vote=personal_vote_s,
            opposite_vote=personal_vote_s,
            keyboard=keyboard,
        )
        mock_view_f.posts.personal.bot.edit_message_reply_markup.acow(
            chat_id=personal_vote_s.user.id,
            message_id=personal_vote_s.message_id,
            reply_markup=ANY,  # self.get_keyboard or shared keyboard `add_btn`
        )
        assert result == mock_view_f.posts.personal.bot.edit_message_reply_markup.return_value

    @staticmethod
    async def test_show(
            mock_view_f: MagicMock,
            mock_personal_post: MagicMock,
            personal_vote_s: model.IPersonalVote,
    ):
        result = await view.Posts.Personal.show(
            self=mock_view_f.posts.personal,
            post=personal_vote_s,
            clicker_vote=personal_vote_s,
            opposite_vote=personal_vote_s,
        )
        mock_view_f.posts.personal.bot.copy_message.acow(
            chat_id=personal_vote_s.user.id,
            from_chat_id=view.PostsChannels.STORE.value,
            message_id=personal_vote_s.message_id,
            reply_markup=mock_view_f.posts.personal.get_keyboard.return_value,
        )
        mock_view_f.posts.personal.get_keyboard.acow(
            post=personal_vote_s,
            clicker_vote=personal_vote_s,
            opposite_vote=personal_vote_s,
        )
        assert result


@pytest.fixture(scope='function', )
def patched_logger() -> MagicMock:
    with patch_object(target=view, attribute='known_exceptions_logger', ) as mock_logger:
        yield mock_logger


async def test_store_in_channel(mock_view_f: MagicMock, ):
    result = await view.Posts.store_in_channel(self=mock_view_f, message_id=1, )
    mock_view_f.bot.copy_message.acow(
        chat_id=view.PostsChannels.STORE.value,
        from_chat_id=mock_view_f.id,
        message_id=1,
    )
    assert result == mock_view_f.bot.copy_message.return_value


async def test_no_mass_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.no_mass_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=view.Texts.Public.NO_MASS_POSTS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_no_new_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.no_new_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=view.Texts.Public.NO_NEW_POSTS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_no_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.no_personal_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.Personal.NO_POSTS,
        reply_markup=view.Keyboards.create_personal_post
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_user_accepted_pers_post_share(mock_view_f: MagicMock, ):
    result = await view.Posts.user_accepted_share_proposal(
        self=mock_view_f,
        accepter_username='foo',
        posts_sender_id=typing_Any,
    )
    mock_view_f.bot.send_message.acow(
        chat_id=typing_Any,
        text=view.Texts.Personal.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_USERNAME='foo', ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_user_accepted_pers_post_request(mock_view_f: MagicMock, ):
    result = await view.Posts.user_accepted_request_proposal(self=mock_view_f, posts_recipient_id=1, )
    mock_view_f.bot.send_message.acow(
        chat_id=1,
        text=view.Texts.Personal.USER_ACCEPTED_REQUEST_PROPOSAL.format(
            ACCEPTER_USERNAME=mock_view_f.user.ptb.name,
        ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_delete_post(mock_view_f: MagicMock, ):
    result = await view.Posts.delete_post(self=mock_view_f, message_id=1, )
    mock_view_f.bot.delete_message.acow(chat_id=mock_view_f.id, message_id=1, )
    assert result == mock_view_f.bot.delete_message.return_value


async def test_here_your_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.here_your_personal_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=view.Texts.Personal.HERE_YOUR_POSTS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_here_post_preview(mock_view_f: MagicMock, ):
    result = await view.Posts.here_post_preview(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.HERE_POST_PREVIEW,
        reply_markup=view.Keyboards.send_cancel,
    )
    assert result == mock_view_f.bot.send_message.return_value


class TestShowPost:
    """test_show_post"""

    @staticmethod
    async def test_public(mock_view_f: MagicMock, mock_voted_public_post: MagicMock, ):
        result = await view.Posts.show_post(self=mock_view_f.posts, post=mock_voted_public_post, )
        mock_view_f.posts.public.show.acow(
            post=mock_voted_public_post.post,
            clicker_vote=mock_voted_public_post.clicker_vote,
        )
        assert result == mock_view_f.posts.public.show.return_value

    @staticmethod
    async def test_personal(mock_view_f: MagicMock, mock_voted_personal_post: MagicMock, ):
        result = await view.Posts.show_post(self=mock_view_f.posts, post=mock_voted_personal_post, )
        mock_view_f.posts.personal.show.acow(
            post=mock_voted_personal_post.post,
            clicker_vote=mock_voted_personal_post.clicker_vote,
            opposite_vote=mock_voted_personal_post.opposite_vote,
        )
        assert result == mock_view_f.posts.personal.show.return_value


class TestShowPosts:
    """test_show_posts"""

    @staticmethod
    async def test_exception(mock_view_f: MagicMock, ):
        mock_view_f.posts.show_post.side_effect = TelegramError('')
        result = await view.Posts.show_posts(self=mock_view_f.posts, posts=[typing_Any, ], )
        mock_view_f.posts.show_post.acow(post=typing_Any, )
        assert result == []

    @staticmethod
    async def test_success(mock_view_f: MagicMock, ):
        result = await view.Posts.show_posts(self=mock_view_f.posts, posts=[typing_Any, ], )
        mock_view_f.posts.show_post.acow(post=typing_Any, )
        assert result == [mock_view_f.posts.show_post.return_value, ]


class TestShowForm:
    """test_show_posts"""

    @staticmethod
    async def test_public(mock_view_f: MagicMock, mock_public_post_form: MagicMock, ):
        result = await view.Posts.show_form(self=mock_view_f.posts, form=mock_public_post_form, )
        mock_view_f.posts.bot.copy_message(
            chat_id=mock_public_post_form.author.id,
            from_chat_id=mock_public_post_form.author.id,
            message_id=mock_public_post_form.message_id,
            reply_markup=view.Keyboards.public_form,
        )
        assert result == mock_view_f.posts.bot.copy_message.return_value

    @staticmethod
    async def test_personal(mock_view_f: MagicMock, mock_personal_post_form: MagicMock, ):
        result = await view.Posts.show_form(self=mock_view_f.posts, form=mock_personal_post_form, )
        mock_view_f.posts.bot.copy_message(
            chat_id=mock_personal_post_form.author.id,
            from_chat_id=mock_personal_post_form.author.id,
            message_id=mock_personal_post_form.message_id,
            reply_markup=view.Keyboards.personal_form,
        )
        assert result == mock_view_f.posts.bot.copy_message.return_value


class TestShare:
    """share"""

    @staticmethod
    async def test_error(
            mock_view_f: MagicMock,
            mock_personal_post: MagicMock,
            mock_user: MagicMock,
            patched_logger: MagicMock,
    ):
        mock_view_f.posts.show_post.side_effect = TelegramError('')
        result = await view.Posts.share_post(
            self=mock_view_f.posts,
            post=mock_personal_post,
            post_sender=mock_user,
            post_recipient=mock_user,
        )
        patched_logger.error.acow(msg=mock_view_f.posts.show_post.side_effect, exc_info=True, )
        mock_user.get_vote.return_value.CRUD.upsert_message_id.assert_not_called()
        assert result is None

    @staticmethod
    async def test_success(
            mock_view_f: MagicMock,
            mock_personal_post: MagicMock,
            mock_user: MagicMock,
    ):
        orig_sender_message_id = orig_recipient_message_id = mock_user.get_vote.return_value.message_id
        await view.Posts.share_post(
            self=mock_view_f.posts,
            post=mock_personal_post,
            post_sender=mock_user,
            post_recipient=mock_user,
        )
        # Check get_vote calls
        assert mock_user.get_vote.call_args_list == [
            call(post=mock_personal_post, ),
            call(post=mock_personal_post, ),
        ]
        assert mock_view_f.posts.delete_post.call_args_list == [
            call(chat_id=mock_user.id, message_id=orig_sender_message_id, ),
            call(chat_id=mock_user.id, message_id=orig_recipient_message_id, ),
        ]
        # Check send calls
        assert mock_view_f.posts.show_post.call_args_list == [
            call(
                post=view.model.VotedPersonalPost(
                    post=mock_personal_post,
                    clicker_vote=mock_user.get_vote.return_value,
                    opposite_vote=mock_user.get_vote.return_value,
                )
            ),
            call(
                post=view.model.VotedPersonalPost(
                    post=mock_personal_post,
                    clicker_vote=mock_user.get_vote.return_value,
                    opposite_vote=mock_user.get_vote.return_value,
                )
            ),
        ]
        # Check upsert_message_id calls
        assert mock_user.get_vote.return_value.upsert_message_id.call_args_list == [call(), call(), ]


async def test_share_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.share_posts(
        self=mock_view_f.posts,
        posts=(typing_Any,),
        sender=typing_Any,
        recipient=typing_Any,
    )
    mock_view_f.posts.share_post.acow(
        post=typing_Any,
        post_sender=typing_Any,
        post_recipient=typing_Any,
    )
    assert result is True


async def test_ask_who_to_request_personal_posts(mock_view_f: MagicMock, ):
    with patch_object(view.Keyboards, 'ask_who_to_request_personal_posts', ) as mock_remove:
        result = await view.Posts.ask_who_to_request_personal_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.Personal.WHO_TO_REQUEST,
        reply_markup=mock_remove.return_value,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_permission_to_share_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.ask_permission_to_share_personal_posts(self=mock_view_f, recipient_id=1, )
    mock_view_f.bot.send_message.acow(
        chat_id=1,
        text=view.Texts.Personal.NOTIFY_REQUEST_PROPOSAL.format(USERNAME=mock_view_f.user.ptb.name, ),
        reply_markup=view.Keyboards.ask_permission_share_personal_post(id=mock_view_f.id, )
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_accept_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.ask_accept_personal_posts(self=mock_view_f, recipient_id=1, )
    mock_view_f.bot.send_message.acow(
        chat_id=1,
        text=view.Texts.Personal.NOTIFY_SHARE_PROPOSAL.format(USERNAME=mock_view_f.user.ptb.name, ),
        reply_markup=view.Keyboards.AcceptPosts.build(sender_id=mock_view_f.id, )
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_personal_post_hello(mock_view_f: MagicMock):
    result = await view.Posts.say_personal_post_hello(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.Personal.HELLO,
        reply_markup=view.Keyboards.say_personal_post_hello,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_public_post_hello(mock_view_f: MagicMock):
    result = await view.Posts.say_public_post_hello(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(text=view.Texts.Public.HELLO, chat_id=mock_view_f.id, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_say_success_post(mock_view_f: MagicMock):
    result = await view.Posts.say_success_post(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(text=view.Texts.CREATED_SUCCESSFULLY, chat_id=mock_view_f.id, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_post_to_vote_not_found(mock_view_f: MagicMock, mock_callback_query: MagicMock, ):
    result = await view.Posts.post_to_vote_not_found(self=mock_view_f, tooltip=mock_callback_query, )
    mock_callback_query.answer.acow(text=view.Texts.POST_TO_VOTE_NOT_FOUND, show_alert=True, )
    assert result == mock_callback_query.answer.return_value


async def test_ask_who_to_share_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.ask_who_to_share_personal_posts(self=mock_view_f)
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.Personal.WHO_TO_SHARE,
        reply_markup=view.Keyboards.request_chat(request_btn_params=dict(request_username=True, request_name=True, ), ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_cant_send_posts_to_user_help_text(mock_view_f: MagicMock, ):
    result = await view.Posts.cant_send_posts_to_user_help_text(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=view.Texts.Personal.CANT_SEND_TO_THIS_USER,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_user_declined_share_proposal(mock_view_f: MagicMock):
    result = await view.Posts.user_declined_share_proposal(self=mock_view_f.posts, posts_sender_id=1, )
    mock_view_f.posts.shared.user_declined_share_proposal.acow(
        id=1,
        decliner_username=mock_view_f.posts.user.ptb.name
    )
    assert result == mock_view_f.posts.shared.user_declined_share_proposal.return_value


async def test_user_declined_request_proposal(mock_view_f: MagicMock):
    result = await view.Posts.user_declined_request_proposal(self=mock_view_f.posts, posts_recipient_id=1, )
    mock_view_f.posts.shared.user_declined_request_proposal.acow(
        id=1,
        decliner_username=mock_view_f.posts.user.ptb.name
    )
    assert result == mock_view_f.posts.shared.user_declined_request_proposal.return_value


async def test_show_pending(mock_view_f: MagicMock, public_post_s: model.IPublicPost, ):
    result = await view.Posts.show_pending(self=mock_view_f.posts, post=public_post_s, )
    mock_view_f.posts.bot.copy_message.acow(
        chat_id=mock_view_f.posts.id,
        from_chat_id=view.PostsChannels.STORE.value,
        message_id=public_post_s.message_id,
        reply_markup=view.Keyboards.ShowPending.update_status(post=public_post_s, )
    )
    assert result == mock_view_f.posts.bot.copy_message.return_value


async def test_voting_internal_error(mock_callback_query: MagicMock, ):
    result = await view.Posts.voting_internal_error(tooltip=mock_callback_query, )
    mock_callback_query.answer.acow(text=view.Texts.INTERNAL_ERROR, show_alert=True, )
    assert result == mock_callback_query.answer.return_value


async def test_sender_has_no_personal_posts(mock_view_f: MagicMock, ):
    result = await view.Posts.sender_has_no_personal_posts(mock_view_f.posts, recipient_id=1, )
    mock_view_f.posts.bot.send_message.acow(chat_id=1, text=view.Texts.Personal.SENDER_HAS_NO_POSTS, )
    assert result == mock_view_f.posts.bot.send_message.return_value


async def test_check_post_existence(mock_view_f: MagicMock, public_post_s: model.IPublicPost, ):
    result = await view.Posts.check_post_existence(self=mock_view_f.posts, post=public_post_s, )
    mock_view_f.posts.shared.check_message_existence.acow(
        chat_id=view.PostsChannels.STORE.value,
        message_id=public_post_s.message_id,
    )
    assert result == mock_view_f.posts.shared.check_message_existence.return_value


async def test_use_get_stats_with_cmd(mock_view_f: MagicMock, ):
    result = await view.Posts.use_get_stats_with_cmd(self=mock_view_f, id=1, )
    mock_view_f.bot.send_message.acow(chat_id=1, text=USE_GET_STATS_WITH_CMD, )
    assert result == mock_view_f.bot.send_message.return_value


class TestKeyboards:
    class TestAcceptPosts:

        @staticmethod
        def test_build_cbk():
            result = view.Keyboards.AcceptPosts.build_cbk(sender_id=1, flag=False, )  # Any flag ok
            assert result == f'{view.Keyboards.AcceptPosts.CBK_PREFIX} 1 0'

        @staticmethod
        def test_build():
            expected_keyboard = tg_IKM.from_row(
                button_row=(
                    tg_IKB(
                        text=view.Keyboards.AcceptPosts.DECLINE_TEXT,
                        callback_data=view.Keyboards.AcceptPosts.build_cbk(sender_id=1, flag=False, )
                    ),
                    tg_IKB(
                        text=view.Keyboards.AcceptPosts.ACCEPT_TEXT,
                        callback_data=view.Keyboards.AcceptPosts.build_cbk(sender_id=1, flag=True, )
                    ),), )
            actual_keyboard = view.Keyboards.AcceptPosts.build(sender_id=1, )
            assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_ask_permission_share_personal_post():
        expected_keyboard = tg_IKM.from_row(
            button_row=(
                tg_IKB(
                    text=view.Texts.Personal.Buttons.DISALLOW,
                    callback_data=f'{view.Cbks.REQUEST_PERSONAL_POSTS} {1} 0'
                ),
                tg_IKB(
                    text=view.Texts.Personal.Buttons.ALLOW,
                    callback_data=f'{view.Cbks.REQUEST_PERSONAL_POSTS} {1} 1'
                ),), )

        result = view.Keyboards.ask_permission_share_personal_post(id=1, )
        assert result == expected_keyboard
