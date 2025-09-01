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

from unittest.mock import ANY
from typing import TYPE_CHECKING, Any as typing_Any

from pytest import mark as pytest_mark

from app.tg.ptb.entities.post import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import UsersShared
    from app.tg.ptb.entities.collection.model import ICollection
    from custom_ptb.callback_context import CallbackContext


class TestCreatePublicPost:

    @staticmethod
    async def test_create_public_post(mock_context: MagicMock, ):
        mock_context.user.is_registered = True
        # Before 
        mock_context.user_data.forms.public_post = None
        # Execution
        result = await handlers.CreatePublicPost.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.view.posts.say_public_post_hello.assert_called_once_with()
        assert result == 0

    @staticmethod
    async def test_sample_handler(
            mock_context: MagicMock,
            mock_update: MagicMock,
            mock_public_post_form: MagicMock,
    ):
        with patch_object(
                target=handlers,
                attribute='PublicPostForm',

                return_value=mock_public_post_form,
        ) as mock_public_post_form_cls:
            result = await handlers.CreatePublicPost.sample_handler(update=mock_update, context=mock_context, )
        mock_public_post_form_cls.assert_called_once_with(
            author=mock_context.user,
            channel_id=mock_update.effective_chat.id,
            message_id=mock_update.message.message_id,
            message=mock_update.message,
        )
        assert mock_context.user_data.forms.public_post == mock_public_post_form_cls.return_value
        mock_context.view.posts.here_post_preview.acow()
        mock_context.view.posts.show_form.acow(
            form=mock_context.user_data.forms.public_post,
        )
        assert result == 1

    @staticmethod
    async def test_post_confirm_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
        mock_update.message.text = 'foo'
        # Execution
        result = await handlers.CreatePublicPost.confirm_handler(update=mock_update, context=mock_context, )
        # Checks
        mock_context.view.warn.incorrect_send.acow()
        assert result is None

    @staticmethod
    async def test_confirm_handler(
            mock_context: MagicMock,
            mock_update: MagicMock,
            patched_logger: MagicMock,
    ):
        """confirm_handler"""
        mock_context.bot_data.inline_data.posts = []
        mock_update.message.text = handlers.CreatePublicPost.SEND_KEYWORD
        mock_form = mock_context.user_data.forms.public_post  # will be cleared after success
        with (
            patch_object(target=handlers, attribute='add_post_to_inline_data', ) as mock_add_post_to_inline_data,
            patch_object(
                target=handlers.SystemService,
                attribute='set_bots_votes_to_post',
                side_effect=Exception,
            ) as mock_set_bot_votes
        ):
            result = await handlers.CreatePublicPost.confirm_handler(update=mock_update, context=mock_context, )
        mock_add_post_to_inline_data.acow(
            inline_data=mock_context.bot_data.inline_data,
            post=mock_form.create.return_value,
        )
        assert result == -1
        mock_context.view.posts.say_success_post.acow()
        mock_form.create.acow()
        mock_set_bot_votes.acow(post=mock_form.create.return_value, )
        patched_logger.error.acow(msg=ANY, exc_info=True, )
        assert mock_context.user_data.forms.public_post is None


class TestCreatePersonalPost:
    """CreatePersonalPost"""

    @staticmethod
    async def test_entry_point(mock_context: MagicMock, ):
        # Before
        mock_context.user_data.forms.personal_post = None
        # Execution
        result = await handlers.CreatePersonalPost.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        assert result == 0
        mock_context.view.posts.say_personal_post_hello.acow()
        # Mock call always the same

    @staticmethod
    async def test_entry_point_handler(
            mock_context: MagicMock,
            mock_update: MagicMock,
            mock_personal_post_form: MagicMock,
    ):
        with patch_object(
                handlers,
                'PersonalPostForm',
                return_value=mock_personal_post_form,
        ) as mock_post_form_cls:
            result = await handlers.CreatePersonalPost.entry_point_handler(update=mock_update, context=mock_context, )
        # Checks
        mock_post_form_cls.acow(
            author=mock_context.user,
            channel_id=mock_update.effective_chat.id,
            message_id=mock_update.message.message_id,
        )
        assert mock_context.user_data.forms.personal_post == mock_post_form_cls.return_value
        mock_context.view.posts.show_form.acow(
            form=mock_context.user_data.forms.personal_post, )
        assert result == 1

    @staticmethod
    async def test_sample_handler_incorrect(mock_context: MagicMock, mock_update: MagicMock, ):
        """sample_handler"""
        mock_update.message.text = 'foo'
        # Execution
        result = await handlers.CreatePersonalPost.post_sample_handler(
            update=mock_update,
            context=mock_context,
        )
        # Checks
        assert result is None
        mock_context.view.warn.incorrect_continue.assert_called_with(
            keyword=handlers.CreatePersonalPost.SEND_KEYWORD
        )

    @staticmethod
    async def test_collection_name_cbk_handler(mock_context: MagicMock, mock_update: MagicMock, ):
        with patch_object(
                target=handlers.CreatePersonalPost.Keyboards,
                attribute='ChooseForPost',
        ) as MockChooseForPostCls:
            MockChooseForPostCls.extract_cbk_data.return_value = ('foo', True,)
            result = await handlers.CreatePersonalPost.collection_name_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
        # Checks
        MockChooseForPostCls.extract_cbk_data.acow(cbk_data=mock_update.callback_query.data, )
        mock_context.user_data.forms.personal_post.handle_collection_name_btn.acow(
            collection_name='foo',
            is_chosen=True,  # Don't forget to swap, by default collection coming unchecked
        )
        mock_context.view.collections.update_chosen_collection.acow(
            collection_name='foo',
            is_chosen=True,
            tooltip=mock_update.callback_query,
            keyboard=MockChooseForPostCls.update_keyboard(
                btn_cbk_data=mock_update.callback_query.data,
                # keyboard need to replicate it cuz building a new one a bit hard cuz building placed in service module
                keyboard=mock_update.effective_message.reply_markup,
            ),
        )
        assert result == 2

    @staticmethod
    async def test_collection_names_text_handler(mock_context: MagicMock, mock_update: MagicMock, ):
        mock_context.user_data.forms.personal_post.collection_names = {1, }
        result = await handlers.CreatePersonalPost.collection_names_text_handler(
            update=mock_update,
            context=mock_context,
        )
        mock_context.user_data.forms.personal_post.handle_collection_names.acow(
            text=mock_update.message.text.strip.return_value,
        )
        mock_context.view.collections.show_chosen_collections_for_post.acow(
            collection_names=mock_context.user_data.forms.personal_post.collection_names,
        )
        assert result is None

    class TestSampleHandler:
        """test_sample_handler"""

        @staticmethod
        async def body(mock_context: MagicMock, mock_update: MagicMock, ):
            assert mock_context.user.collections == []
            mock_update.message.text = handlers.CreatePersonalPost.SEND_KEYWORD
            # Execution
            result = await handlers.CreatePersonalPost.post_sample_handler(
                update=mock_update,
                context=mock_context,
            )
            # Checks
            assert result == 2
            mock_context.user.get_collections.acow(cache=True, )
            mock_context.user.get_collections.reset_mock()

        async def test_collections_names_from_db(
                self,
                mock_context: MagicMock,
                mock_update: MagicMock,
                collection_s: ICollection,
        ):
            mock_context.user.get_collections.return_value = {collection_s, }
            # Execution
            await self.body(mock_context=mock_context, mock_update=mock_update, )
            mock_context.view.collections.propose_collections_for_post.acow(
                collections={collection_s, },
            )

        async def test_default_collections_names(
                self,
                mock_context: MagicMock,
                mock_update: MagicMock,
                collection_s: ICollection,
        ):
            # Execution
            await self.body(mock_context=mock_context, mock_update=mock_update, )
            mock_context.view.collections.propose_collections_for_post.acow(
                collections=mock_context.user.get_collections.return_value,
            )

    @staticmethod
    async def test_confirm_handler(mock_context: MagicMock, ):
        """confirm_handler"""
        # Create alias cuz forms.personal_post will be None after test but alias preserves ref to post form
        orig_form = mock_context.user_data.forms.personal_post
        # Execution
        result = await handlers.CreatePersonalPost.confirm_handler(_=typing_Any, context=mock_context, )
        assert result == -1
        mock_context.view.posts.say_success_post.acow()
        orig_form.create.acow()
        assert mock_context.user_data.forms.personal_post is None


class TestSharePersonalPosts:
    class_to_test = handlers.SharePersonalPosts

    async def test_entry_point_no_posts(self, mock_context: MagicMock, ):
        with patch_object(
                mock_context.user,
                'get_personal_posts',
                return_value=[],
        ) as mock_get_personal_posts:
            result = await self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        mock_get_personal_posts.acow()
        mock_context.view.posts.no_personal_posts.acow()
        assert result == -1

    async def test_entry_point(self, mock_context: MagicMock, ):
        result = await self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        mock_context.user.get_personal_posts.acow()
        mock_context.view.posts.ask_who_to_share_personal_posts.acow()
        assert result == 0

    class TestRecipientHandler:
        """test_recipient_handler"""
        class_to_test = handlers.SharePersonalPosts

        async def test_incorrect(
                self,
                mock_context: CallbackContext,
                mock_update: MagicMock,
        ):
            mock_update.message.text = 'foo'
            with patch_object(
                    target=handlers,
                    attribute='custom_request_user',
                    return_value=None,
            ) as mock_request_user:
                result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_request_user.acow(
                app=mock_context.application,
                message=mock_update.effective_message
            )
            mock_context.view.warn.incorrect_user.acow()
            assert result is None

        async def test_user_not_found(self, mock_context: MagicMock, mock_update: MagicMock, ):
            mock_context.view.posts.ask_accept_personal_posts.side_effect = handlers.TelegramError('')
            with patch_object(target=handlers, attribute='custom_request_user', ) as mock_request_user:
                result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_request_user.acow(
                app=mock_context.application,
                message=mock_update.effective_message,
            )
            mock_context.view.posts.ask_accept_personal_posts.acow(
                recipient_id=mock_request_user.return_value.user_id,
            )
            mock_context.view.user_not_found.acow()
            assert result is None

        # Both contact and text are the same test
        async def test_success(self, mock_context: MagicMock, mock_update: MagicMock, ):
            with patch_object(target=handlers, attribute='custom_request_user', ) as mock_request_user:
                result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_request_user.acow(
                app=mock_context.application,
                message=mock_update.effective_message,
            )
            mock_context.view.posts.ask_accept_personal_posts.acow(
                recipient_id=mock_request_user.return_value.user_id,
            )
            mock_context.view.say_user_got_share_proposal.acow(
                shared_recipient=mock_request_user.return_value,
            )
            # Need 2 calls for logic
            assert result == -1

    class TestSharePersonalPostCbkHandler:
        """SharePersonalPostCbkHandler"""

        @staticmethod
        async def test_accept_button(
                mock_update: MagicMock,
                mock_context: MagicMock,
                mock_user: MagicMock,
                patched_personal_post_cls: MagicMock,
        ):
            """recipient_decision_cbk_handler"""
            patched_personal_post_cls.extract_cbk_data.return_value = [mock_user, None, ]
            mock_posts_sender = patched_personal_post_cls.extract_cbk_data.return_value[0]
            mock_context.user.is_registered = True
            patched_personal_post_cls.extract_cbk_data.return_value = [mock_posts_sender, True, ]
            # Execution
            await handlers.SharePersonalPosts.recipient_decision_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
            # Checks
            patched_personal_post_cls.extract_cbk_data.acow(
                callback_data=mock_update.callback_query.data
            )
            mock_context.view.posts.user_accepted_share_proposal.acow(
                accepter_username=mock_context.user.ptb.name,
                posts_sender_id=mock_posts_sender.id,
            )
            mock_context.view.posts.share_posts(
                sender=mock_posts_sender,
                recipient=mock_context.user,
            )
            # Check 2 calls view.posts.use_get_stats_with_cmd for sender and recipient (same func with different args)
            mock_context.view.posts.use_get_stats_with_cmd.assert_any_call(
                id=mock_posts_sender.id,
            )
            mock_context.view.posts.use_get_stats_with_cmd.assert_any_call(
                id=mock_context.user.id
            )
            assert mock_context.view.posts.use_get_stats_with_cmd.call_count == 2
            # Finally block
            mock_context.view.posts.remove_sharing_message.acow(
                message=mock_update.effective_message,
            )
            mock_update.callback_query.answer.acow()

        @staticmethod
        async def test_decline_button(
                mock_update: MagicMock,
                mock_context: MagicMock,
        ):
            """recipient_decision_cbk_handler"""
            user_id = 1
            mock_context.user.is_registered = True
            mock_update.callback_query.data = f'_ {user_id} 0'
            await handlers.SharePersonalPosts.recipient_decision_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
            mock_context.view.posts.user_declined_share_proposal.acow(
                posts_sender_id=user_id,
            )
            # Finally block
            mock_context.view.posts.remove_sharing_message.acow(
                message=mock_update.effective_message,
            )
            mock_update.callback_query.answer.acow()


class TestRequestPersonalPosts:
    cls_to_test = handlers.RequestPersonalPosts

    async def test_entry_point(self, mock_context: MagicMock, ):
        # Execution
        result = await self.cls_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.view.posts.ask_who_to_request_personal_posts.acow()
        assert result == 0

    async def test_not_found(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
            users_shared: UsersShared,
    ):
        mock_update.effective_message.users_shared = users_shared
        mock_context.view.posts.ask_permission_to_share_personal_posts.side_effect = (
            handlers.TelegramError('')
        )
        result = await self.cls_to_test.recipient_handler(update=mock_update, context=mock_context, )
        mock_context.view.user_not_found.acow()
        assert result is None

    async def test_success(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
            users_shared: UsersShared,
    ):
        mock_update.effective_message.users_shared = users_shared
        result = await self.cls_to_test.recipient_handler(update=mock_update, context=mock_context, )
        mock_context.view.posts.ask_permission_to_share_personal_posts.acow(
            recipient_id=users_shared.users[0].user_id,
        )
        mock_context.view.say_user_got_request_proposal.acow(
            shared_recipient=users_shared.users[0],
        )
        assert result == -1

    class TestRequestPersonalPostCbkHandler:
        """request_personal_post_cbk_handler"""

        @staticmethod
        async def body(
                mock_update: MagicMock,
                mock_context: MagicMock,
                mock_personal_post: MagicMock,
        ):
            await handlers.RequestPersonalPosts.recipient_decision_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
            # Checks
            mock_personal_post.extract_cbk_data.acow(
                callback_data=mock_update.callback_query.data,
            )
            mock_context.view.posts.remove_sharing_message.acow(
                message=mock_update.effective_message,
            )
            mock_update.callback_query.answer.assert_called_once()

        async def accept_body(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                mock_personal_post: MagicMock,
        ):
            mock_personal_post.extract_cbk_data.return_value = [mock_context.user, True, ]
            await self.body(
                mock_update=mock_update,
                mock_context=mock_context,
                mock_personal_post=mock_personal_post,
            )
            mock_context.view.posts.share_posts(
                sender=mock_context.user,
                recipient=mock_context.user,
            )

        @pytest_mark.skip(reason='Removed method')
        async def test_error(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_personal_post_cls: MagicMock,
                mock_bot: MagicMock,
                patched_logger: MagicMock,
        ):
            patched_personal_post_cls.extract_cbk_data.side_effect = Exception
            await self.body(
                mock_update=mock_update,
                mock_context=mock_context,
                mock_personal_post=patched_personal_post_cls,
            )
            patched_logger.error.assert_called_once()
            mock_context.view.internal_error.acow()

        async def test_decline_button(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_personal_post_cls: MagicMock,
                mock_bot: MagicMock,
        ):
            mock_recipient = mock_context.user
            patched_personal_post_cls.extract_cbk_data.return_value = [mock_recipient, False, ]
            # Execution
            await self.body(
                mock_update=mock_update,
                mock_context=mock_context,
                mock_personal_post=patched_personal_post_cls,
            )
            # Checks
            mock_context.view.posts.user_declined_request_proposal.acow(
                posts_recipient_id=mock_recipient.id
            )

        async def test_no_sender_posts(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_personal_post_cls: MagicMock,
                mock_bot: MagicMock,
        ):
            mock_context.view.posts.share_posts.return_value = False
            # Execution
            await self.accept_body(
                mock_update=mock_update,
                mock_context=mock_context,
                mock_personal_post=patched_personal_post_cls,
            )
            # Checks
            mock_context.view.posts.no_personal_posts.acow()
            mock_context.view.posts.sender_has_no_personal_posts.acow(
                recipient_id=mock_context.user.id,
            )

        async def test_accept_button(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                patched_personal_post_cls: MagicMock,
                mock_bot: MagicMock,
        ):
            # Execution
            await self.accept_body(
                mock_update=mock_update,
                mock_context=mock_context,
                mock_personal_post=patched_personal_post_cls,
            )
            # Checks
            mock_context.view.posts.user_accepted_request_proposal.acow(
                posts_recipient_id=mock_context.user.id,
            )


class TestGetMyPersonalPostsCmd:
    @staticmethod
    async def test_no_posts(mock_update: MagicMock, mock_context: MagicMock, ):
        mock_context.user.get_personal_posts.return_value = []
        result = await handlers.get_my_personal_posts(_=mock_update, context=mock_context, )
        mock_context.view.posts.no_personal_posts.acow()
        assert result is None

    @staticmethod
    async def test_success(mock_update: MagicMock, mock_context: MagicMock, ):
        with patch_object(handlers.model.VotedPersonalPost, 'from_posts', ) as mock_from_posts:
            result = await handlers.get_my_personal_posts(_=mock_update, context=mock_context, )
        mock_from_posts.acow(
            posts=mock_context.user.get_personal_posts(),
            clicker=mock_context.user,
            opposite=mock_context.user,
        )
        mock_context.view.posts.here_your_personal_posts.acow()
        mock_context.view.posts.show_posts.acow(posts=mock_from_posts.return_value)
        assert result is None

    class TestGetPublicPostCmd:

        @staticmethod
        async def test_no_mass_posts(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_context.user.get_new_public_post.return_value = None
            result = await handlers.get_public_post(_=mock_update, context=mock_context, )
            # Checks
            mock_context.user.get_new_public_post.acow()
            mock_context.view.posts.no_mass_posts.acow()
            assert result is None

        @staticmethod
        async def test_no_new_posts(mock_update: MagicMock, mock_context: MagicMock, ):
            mock_context.user.get_new_public_post.return_value = []
            mock_context.user.matcher.is_user_has_covotes = True
            # EXECUTION
            result = await handlers.get_public_post(_=mock_update, context=mock_context, )
            mock_context.user.get_new_public_post.acow()
            mock_context.view.posts.no_new_posts.acow()
            assert result is None

        @staticmethod
        async def test_success(mock_update: MagicMock, mock_context: MagicMock, ):
            result = await handlers.get_public_post(_=mock_update, context=mock_context, )
            mock_context.user.get_new_public_post.assert_called_once_with()
            mock_context.view.posts.show_post.assert_called_once_with(
                post=mock_context.user.get_new_public_post.return_value,
            )
            mock_context.user.upsert_shown_post.assert_called_once_with(
                message_id=mock_context.view.posts.show_post.return_value.message_id,
                public_post=mock_context.user.get_new_public_post.return_value,
            )
            assert result is None

        class TestUpdatePublicPostStatusCbkHandler:
            """update_public_post_status_cbk"""

            @staticmethod
            @pytest_mark.parametrize(argnames='status', argvalues=handlers.model.PublicPost.Status)
            async def test_pending_button(
                    mock_update: MagicMock,
                    mock_context: MagicMock,
                    status: handlers.model.PublicPost.Status,
            ):
                post_id = 1
                mock_update.callback_query.data = f'_ {post_id} {status}'
                with patch_object(handlers.model, 'PublicPost', ) as mock_PublicPost:
                    result = await handlers.update_public_post_status_cbk(
                        update=mock_update,
                        context=mock_context,
                    )
                mock_PublicPost.read.acow(post_id=post_id, connection=mock_context.connection, )
                mock_PublicPost.read.return_value.Status.acow(status)
                mock_PublicPost.read.return_value.update_status.acow(
                    status=mock_PublicPost.read.return_value.Status.return_value
                )
                mock_context.view.say_ok.acow()
                assert result == mock_update.callback_query.answer.return_value
