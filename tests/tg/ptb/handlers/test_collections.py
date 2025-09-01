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

from typing import TYPE_CHECKING, Any as typing_Any

from app.tg.ptb.entities.collection import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram import UsersShared
    from app.tg.ptb.entities.collection.model import ICollection
    from app.tg.ptb.entities.post.model import IPublicPost


class TestGetMyCollections:
    @staticmethod
    async def test_no_collections(mock_context: MagicMock, ):
        mock_context.user.get_collections.return_value = []
        await handlers.get_my_collections_handler_cmd(_=typing_Any, context=mock_context, )
        mock_context.user.get_collections.acow()
        mock_context.view.collections.no_collections.acow()

    @staticmethod
    async def test_success(mock_context: MagicMock, ):
        await handlers.get_my_collections_handler_cmd(_=typing_Any, context=mock_context, )
        mock_context.user.get_collections.acow()
        mock_context.view.collections.show_my_collections.acow(
            collections=mock_context.user.get_collections.return_value,
        )


class TestSharePersonalCollections:
    """CreatePersonalPost"""

    class AttrsForInnerClasses:
        class_to_test = handlers.SharePersonalCollections

    class_to_test = AttrsForInnerClasses.class_to_test

    async def test_entry_point_no_collections(self, mock_context: MagicMock, ):
        mock_context.user.get_collections.return_value = []
        # Execution
        result = await self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.view.collections.no_collections.acow()
        assert result == -1

    async def test_entry_point(self, mock_context: MagicMock, ):
        # Execution
        result = await self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.user.get_collections.acow(cache=True, )
        mock_context.view.collections.show_collections.acow(
            collections=mock_context.user.get_collections.return_value,
            text=handlers.Texts.ASK_TO_SHARE,
            keyboard=handlers.ViewKeyboards.Inline.Mark,
        )
        mock_context.view.notify_ready_keyword.acow()
        assert result == 0

    async def test_mark_to_share_cbk_handler(self, mock_update: MagicMock, mock_context: MagicMock, ):
        """mark_show_cbk_handler"""
        collection_id = 1
        mock_update.callback_query.data = f'_ {collection_id}'
        mock_context.user_data.tmp_data.collections_to_share.ids = set()
        # Test Added
        result = await self.class_to_test.mark_to_share_cbk_handler(update=mock_update, context=mock_context, )
        assert mock_context.user_data.tmp_data.collections_to_share.ids == {collection_id, }
        assert result is None
        # And removed
        result = await self.class_to_test.mark_to_share_cbk_handler(update=mock_update, context=mock_context, )
        assert mock_context.user_data.tmp_data.collections_to_share.ids == set()
        assert result is None

    async def test_continue_handler_incorrect(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
    ):
        """test_continue_handler"""
        result = await self.class_to_test.continue_handler(update=mock_update, context=mock_context, )
        # Checks
        mock_context.view.warn.incorrect_finish.acow()
        assert result is None

    async def test_continue_handler_collections_not_chosen(
            self,
            mock_update: MagicMock,
            mock_context: MagicMock,
    ):
        """test_continue_handler"""
        mock_update.message.text = handlers.Texts.FINISH_KEYWORD
        mock_context.user_data.tmp_data.collections_to_share.ids = set()
        # Execution
        result = await self.class_to_test.continue_handler(update=mock_update, context=mock_context, )
        # Checks
        mock_context.view.collections.collections_to_share_not_chosen.acow(
            reply_to_message_id=mock_context.user_data.tmp_data.collections_to_share.message_id_with_collections,
        )
        assert result is None

    async def test_continue_handler(self, mock_update: MagicMock, mock_context: MagicMock, ):
        """test_continue_handler"""
        mock_update.message.text = handlers.Texts.FINISH_KEYWORD
        mock_context.user_data.tmp_data.collections_to_share.ids = {1, 2, 3}
        # Execution
        result = await self.class_to_test.continue_handler(update=mock_update, context=mock_context, )
        # Checks
        mock_context.view.collections.ask_who_to_share.acow()
        assert result == 1

    class TestRecipientHandler(AttrsForInnerClasses):
        """test_recipient_handler"""

        async def test_shared_recipient_is_none(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
        ):
            with patch_object(handlers, 'extract_passed_user', return_value=None, ) as mock_extract_passed_user:
                result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_extract_passed_user.acow(
                update=mock_update,
                context=mock_context,
                new_version=True,
            )
            mock_context.view.user_not_found.acow()
            assert result is None

        async def test_recipient_not_found(
                self,
                mock_update: MagicMock,
                mock_context: MagicMock,
                users_shared: UsersShared,
        ):
            mock_update.effective_message.users_shared = users_shared
            mock_context.view.collections.ask_accept_collections.side_effect = handlers.TelegramError('')
            result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_context.view.collections.ask_accept_collections.acow(
                recipient_id=users_shared.users[0].user_id,
                collections_ids=mock_context.user_data.tmp_data.collections_to_share.ids,
            )
            mock_context.view.user_not_found.acow()
            assert result is None

        async def test_success(self, mock_update: MagicMock, mock_context: MagicMock, users_shared: UsersShared, ):
            orig_collections_to_share = mock_context.user_data.tmp_data.collections_to_share
            mock_update.effective_message.users_shared = users_shared
            result = await self.class_to_test.recipient_handler(update=mock_update, context=mock_context, )
            mock_context.view.collections.ask_accept_collections.acow(
                recipient_id=users_shared.users[0].user_id,
                collections_ids=orig_collections_to_share.ids,
            )
            mock_context.view.say_user_got_share_proposal.acow(
                shared_recipient=users_shared.users[0],
            )
            assert mock_context.user_data.tmp_data.collections_to_share is None
            assert result == -1

    class TestAcceptCollectionsCbk(AttrsForInnerClasses):
        async def test_declined(self, mock_context: MagicMock, mock_update: MagicMock, ):
            """accept_collections_cbk"""
            mock_update.callback_query.data = f'_ 1 0'  # user_id, flag
            # Execution
            await self.class_to_test.recipient_decision_cbk_handler(update=mock_update, context=mock_context, )
            # Checks
            mock_context.view.collections.recipient_declined_share_proposal.acow(
                sender_id=1,
            )
            mock_update.callback_query.answer.acow()

        async def test_collections_not_exists(self, mock_context: MagicMock, mock_update: MagicMock, ):
            """accept_collections_cbk"""
            mock_update.callback_query.data = f'_ 1 2 3'
            # Execution
            with patch_object(
                    target=handlers.CollectionService,
                    attribute='get_by_ids',
                    return_value=[],
            ) as mock_get_by_ids:
                await self.class_to_test.recipient_decision_cbk_handler(update=mock_update, context=mock_context, )
            mock_get_by_ids.acow(ids=[3, ], user=mock_context.user, )
            mock_update.callback_query.answer.acow()

        async def test_accepted(
                self,
                mock_context: MagicMock,
                mock_update: MagicMock,
                collection_s: ICollection,
        ):
            """accept_collections_cbk_handler"""
            mock_update.callback_query.data = f'_ 1 2 3'
            mock_context.user_data.tmp_data.collections_to_share.ids = {1, 2, 3}
            # Execution
            with patch_object(
                    target=handlers.CollectionService,
                    attribute='get_by_ids',
                    return_value=[collection_s],
            ) as mock_get_by_ids:
                await self.class_to_test.recipient_decision_cbk_handler(update=mock_update, context=mock_context, )
            # Checks
            mock_get_by_ids.acow(ids=[3, ], user=mock_context.user, )
            mock_context.view.collections.show_shared_collections.acow(
                sender_id=int(mock_update.effective_user.id),
                collections=[collection_s],
            )
            mock_update.callback_query.answer.acow()

    async def test_show_collection_posts_to_recipient_cbk_handler(
            self,
            mock_context: MagicMock,
            mock_update: MagicMock,
            mock_user: MagicMock,
            public_post_s: IPublicPost,
    ):
        with (
            patch_object(
                target=handlers.ViewKeyboards.Inline.ShowPostsToRecipient,
                attribute='extract_cbk_data',
                return_value=(mock_user, 2,),
            ) as mock_extract_cbk_data,
            patch_object(
                target=handlers.Collection,
                attribute='get_posts',
                return_value=[public_post_s, ],
            ) as mock_get_posts,
        ):
            await self.class_to_test.show_collection_posts_to_recipient_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
        mock_extract_cbk_data.acow(
            cbk_data=mock_update.callback_query.data,
            user=mock_context.user,
        )
        mock_get_posts.acow(collection_id=2, connection=mock_context.connection, )
        mock_context.view.collections.show_collection_posts.acow(
            tooltip=mock_update.callback_query,
            posts=handlers.VotedPost.from_posts(
                posts=mock_get_posts.return_value,
                clicker=mock_context.user,
                opposite=mock_user,
            ),
        )
        mock_update.callback_query.answer.acow()


async def test_show_collection_posts_cbk_handler(
        mock_context: MagicMock,
        mock_update: MagicMock,
        public_post_s: IPublicPost,
):
    with (
        patch_object(
            target=handlers.ViewKeyboards.Inline.ShowCollections,
            attribute='extract_cbk_data',
            return_value=1,
        ) as mock_extract_cbk_data,
        patch_object(
            target=handlers.Collection,
            attribute='get_posts',
            return_value=[public_post_s, ],
        ) as mock_get_posts,
    ):
        await handlers.show_collection_posts_cbk_handler(update=mock_update, context=mock_context, )
    mock_extract_cbk_data.acow(cbk_data=mock_update.callback_query.data, )
    mock_get_posts.acow(collection_id=1, connection=mock_context.connection, )
    mock_context.view.collections.show_collection_posts.acow(
        tooltip=mock_update.callback_query,
        posts=handlers.VotedPost.from_posts(
            posts=mock_get_posts.return_value,
            clicker=mock_context.user,
        ),
    )
    mock_update.callback_query.answer.acow()
