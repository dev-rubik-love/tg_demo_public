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
from unittest.mock import MagicMock
from typing import TYPE_CHECKING, Any as typing_Any, Type

import pytest
from telegram.constants import ParseMode
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

from app.tg.ptb.entities.collection import model, view
from app.tg.ptb.entities.collection.texts import Collections as Texts

from tests.tg.ptb.conftest import collection_s
from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from faker import Faker
    from app.tg.ptb.structures import IKeyboard as IStructuresKeyboard
    from app.tg.ptb.entities.collection.model import ICollection
    from app.tg.ptb.entities.post.model import IVotedPublicPost, IPublicPost
    from app.tg.ptb.entities.user.model import IUser


async def test_no_collections(mock_view_f: MagicMock, ):
    result = await view.Collections.no_collections(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.NO_COLLECTIONS,
        reply_markup=view.Keyboards.create_personal_post
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_propose_collections_for_post(mock_view_f: MagicMock, ):
    await view.Collections.propose_collections_for_post(self=mock_view_f.collections, collections=typing_Any, )
    mock_view_f.collections.bot.send_message.acow(
        chat_id=mock_view_f.collections.id,
        text=view.Texts.ASK_FOR_NAMES,
        reply_markup=view.SharedKeyboards.cancel_factory(
            buttons=(view.SharedWords.READY,),
            one_time_keyboard=False,  # Keep keyboard otherwise it will be hidden when user start typing
        ), )
    mock_view_f.collections.show_collections.acow(
        collections=typing_Any,
        text=Texts.HERE_YOUR_COLLECTIONS,
        keyboard=view.Keyboards.Inline.ChooseForPost,
    )


@pytest.mark.parametrize(
    argnames='keyboard',
    argvalues=(
            view.Keyboards.Inline.ShowCollections,
            view.Keyboards.Inline.MarkAndShow,
            view.Keyboards.Inline.Mark,
            view.Keyboards.Inline.ChooseForPost,
    ),
)
async def test_show_collections(
        mock_view_f: MagicMock,
        keyboard: Type[IStructuresKeyboard],
        collection_s: ICollection,
):
    collections = [collection_s] * 5
    inline_keyboard = view.CustomInlineKeyboardMarkup.split(
        buttons=[keyboard.build_inline_button(collection=collection, ) for collection in collections],
        btns_in_row=2,
    )
    result = await view.Collections.show_collections(
        self=mock_view_f,
        collections=collections,
        text='foo',
        keyboard=keyboard,
        posts_in_row=2,
    )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text='foo',
        reply_markup=tg_IKM(inline_keyboard=inline_keyboard, ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_shared_collections(mock_view_f: MagicMock, collection_s: ICollection, ):
    collections = [collection_s, ] * 5
    sender_id = 1
    inline_keyboard = view.CustomInlineKeyboardMarkup.split(
        inline_keyboard=[[view.Keyboards.Inline.ShowPostsToRecipient.build_inline_button(
            collection=collection,
            sender_id=sender_id,
        ) for collection in collections]],
        btns_in_row=2,
    )
    result = await view.Collections.show_shared_collections(
        self=mock_view_f,
        sender_id=sender_id,
        collections=collections,
    )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.HERE_SHARED,
        reply_markup=tg_IKM(inline_keyboard=inline_keyboard, ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_ask_collections(mock_view_f: MagicMock, ):
    result = await view.Collections.ask_collections(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.ASK_TO_SHARE,
        reply_markup=view.Keyboards.skip_cancel,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_show_chosen_collections_for_post(mock_view_f: MagicMock, ):
    result = await view.Collections.show_chosen_collections_for_post(
        self=mock_view_f,
        collection_names={'foo', },
    )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=f'{Texts.SAY_CHOSE_FOR_POST}\n<code><i>foo</i></code>.',  # Remember, set is unordered
        reply_markup=view.Keyboards.show_chosen_collections_for_post,
        parse_mode=ParseMode.HTML,
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_here_collection_posts(mock_view_f: MagicMock, ):
    result = await view.Collections.here_collection_posts(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(chat_id=mock_view_f.id, text=Texts.HERE_POSTS, )
    assert result == mock_view_f.bot.send_message.return_value


async def test_posts_not_found(mock_view_f: MagicMock, mock_callback_query: MagicMock, ):
    result = await view.Collections.posts_not_found(self=mock_view_f, tooltip=mock_callback_query, )
    mock_callback_query.answer.acow(text=Texts.COLLECTION_POSTS_NOT_FOUND, show_alert=True)
    assert result == mock_callback_query.answer.return_value


async def test_few_posts_not_found(mock_view_f: MagicMock, mock_callback_query: MagicMock, ):
    result = await view.Collections.few_posts_not_found(self=mock_view_f, tooltip=mock_callback_query, num=1, )
    mock_callback_query.answer.acow(text=Texts.FEW_POSTS_NOT_FOUND.format(NUM=1), show_alert=True)
    assert result == mock_callback_query.answer.return_value


@pytest.mark.parametrize(argnames='is_exists', argvalues=(True, False,))
async def test_check_collection_posts_existence(
        mock_view_f: MagicMock,
        voted_public_post: IVotedPublicPost,
        is_exists: bool,
):
    mock_view_f.collections.posts_view.check_post_existence.return_value = is_exists
    result = await view.Collections.check_collection_posts_existence(
        self=mock_view_f.collections,
        posts=[voted_public_post, ],
    )
    mock_view_f.collections.posts_view.check_post_existence.acow(post=voted_public_post.post, )
    assert result is is_exists


async def test_ask_accept_collections(mock_view_f: MagicMock, ):
    result = await view.Collections.ask_accept_collections(
        self=mock_view_f,
        recipient_id=1,
        collections_ids={1, 2, 3, },
    )
    mock_view_f.bot.send_message.acow(
        chat_id=1,
        text=Texts.NOTIFY_SHARE_PROPOSAL.format(USERNAME=mock_view_f.user.ptb.name, COUNT=3, ),
        reply_markup=tg_IKM(
            ((
                 tg_IKB(
                     text=Texts.Buttons.DECLINE,
                     callback_data=f'{view.Cbks.ACCEPT_COLLECTIONS} {mock_view_f.id} 0',
                 ),
                 tg_IKB(
                     text=Texts.Buttons.ACCEPT,
                     callback_data=f'{view.Cbks.ACCEPT_COLLECTIONS} {mock_view_f.id} 1 1 2 3',
                 ),
             ),
             (view.SharedKeyboards.get_show_profile_btn(user_id=mock_view_f.id, ),),)
        ),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_no_posts_in_collection(mock_view_f: MagicMock, mock_callback_query: MagicMock, ):
    result = await view.Collections.no_posts_in_collection(self=mock_view_f, tooltip=mock_callback_query, )
    mock_callback_query.answer.acow(text=Texts.NO_POSTS, show_alert=True, )
    assert result == mock_callback_query.answer.return_value


async def test_ask_who_to_share(mock_view_f: MagicMock, ):
    result = await view.Collections.ask_who_to_share(self=mock_view_f, )
    mock_view_f.bot.send_message.acow(
        chat_id=mock_view_f.id,
        text=Texts.WHO_TO_SHARE,
        reply_markup=view.Keyboards.request_user(),
    )
    assert result == mock_view_f.bot.send_message.return_value


async def test_collections_to_share_not_chosen(mock_view_f: MagicMock, ):
    result = await view.Collections.collections_to_share_not_chosen(self=mock_view_f, reply_to_message_id=1, )
    mock_view_f.bot.send_message.acow(
        text=Texts.COLLECTIONS_TO_SHARE_NOT_CHOSE,
        chat_id=mock_view_f.id,
        reply_markup=view.Keyboards.collections_to_share_not_chosen,
        reply_to_message_id=1,
    )
    assert result == mock_view_f.bot.send_message.return_value


class TestShowCollectionPosts:
    """test_show_collection_posts"""

    @staticmethod
    async def test_no_posts_in_collection(mock_view_f: MagicMock, ):
        await view.Collections.show_collection_posts(self=mock_view_f.collections, posts=[], tooltip=typing_Any, )
        mock_view_f.collections.no_posts_in_collection.acow(tooltip=typing_Any, )

    @staticmethod
    async def test_collection_posts_not_found_pre_check(mock_view_f: MagicMock, ):
        """collection_posts_not_found"""
        mock_view_f.collections.check_collection_posts_existence.return_value = False
        await view.Collections.show_collection_posts(
            self=mock_view_f.collections,
            posts=[typing_Any, ],
            tooltip=typing_Any,
        )
        mock_view_f.collections.posts_not_found.acow(tooltip=typing_Any, )

    @staticmethod
    async def test_with_posts(mock_view_f: MagicMock, public_post_s: IPublicPost, ):
        await view.Collections.show_collection_posts(
            self=mock_view_f.collections,
            posts=[public_post_s, ],
            tooltip=typing_Any,
        )
        mock_view_f.collections.here_collection_posts.acow()
        mock_view_f.collections.posts_view.show_posts.acow(posts=[public_post_s], )

    @staticmethod
    async def test_posts_not_found_post_check(mock_view_f: MagicMock, ):
        """test_posts_not_found"""
        mock_view_f.collections.check_collection_posts_existence.return_value = True  # True for post check
        mock_view_f.collections.posts_view.show_posts.return_value = []
        await view.Collections.show_collection_posts(
            self=mock_view_f.collections,
            posts=[typing_Any, ],
            tooltip=typing_Any,
        )
        mock_view_f.collections.posts_not_found.acow(tooltip=typing_Any, )

    @staticmethod
    async def test_few_posts_not_found(mock_view_f: MagicMock, ):
        posts = [typing_Any, typing_Any, ]
        missed_posts_count = 1
        # Will work anyway but better keep; Should be less
        mock_view_f.collections.posts_view.show_posts.return_value = posts[:-missed_posts_count]
        await view.Collections.show_collection_posts(self=mock_view_f.collections, posts=posts, tooltip=typing_Any, )
        mock_view_f.collections.few_posts_not_found.acow(num=missed_posts_count, tooltip=typing_Any, )

    @staticmethod
    async def test_add_close_btn_public_post(
            mock_view_f: MagicMock,
            mock_voted_public_post: MagicMock,
            mock_message: MagicMock,
    ):
        mock_view_f.collections.posts_view.show_posts.return_value = [mock_message]
        await view.Collections.show_collection_posts(
            self=mock_view_f.collections,
            posts=[mock_voted_public_post],
            tooltip=typing_Any,
        )
        mock_view_f.collections.shared.add_close_btn.acow(
            keyboard=mock_view_f.collections.posts_view.public.get_keyboard.return_value,
            message_ids_to_close=[
                mock_view_f.collections.here_collection_posts.return_value,
                *mock_view_f.collections.posts_view.show_posts.return_value,
            ],
        )

    @staticmethod
    async def test_add_close_btn_personal_post(
            mock_view_f: MagicMock,
            mock_voted_personal_post: MagicMock,
            mock_message: MagicMock,
    ):
        mock_view_f.collections.posts_view.show_posts.return_value = [mock_message]
        await view.Collections.show_collection_posts(
            self=mock_view_f.collections,
            posts=[mock_voted_personal_post],
            tooltip=typing_Any,
        )
        mock_view_f.collections.shared.add_close_btn.acow(
            keyboard=mock_view_f.collections.posts_view.personal.get_keyboard.return_value,
            message_ids_to_close=[
                mock_view_f.collections.here_collection_posts.return_value,
                *mock_view_f.collections.posts_view.show_posts.return_value,
            ],
        )


async def test_show_my_collections(mock_view_f: MagicMock, collection_s: ICollection, ):
    result = await view.Collections.show_my_collections(
        self=mock_view_f.collections,
        collections=[collection_s, ],
    )
    mock_view_f.collections.show_collections.acow(
        collections=[collection_s, ],
        text=Texts.HERE_YOUR_COLLECTIONS,
        keyboard=view.Keyboards.Inline.ShowCollections,
    )
    assert result == mock_view_f.collections.show_collections.return_value


async def test_shared_collections_not_found(mock_view_f: MagicMock, ):
    result = await view.Collections.shared_collections_not_found(self=mock_view_f.collections, )
    mock_view_f.collections.bot.send_message.acow(
        text=Texts.SHARED_COLLECTIONS_NOT_FOUND,
        chat_id=mock_view_f.collections.id,
    )
    assert result == mock_view_f.collections.bot.send_message.return_value


async def test_recipient_accepted_share_proposal(mock_view_f: MagicMock, ):
    await view.Collections.recipient_accepted_share_proposal(self=mock_view_f.collections, sender_id=1, )
    mock_view_f.collections.bot.send_message.acow(
        chat_id=1,
        text=Texts.USER_ACCEPTED_SHARE_PROPOSAL.format(
            ACCEPTER_USERNAME=mock_view_f.collections.user.ptb.name,
        ), )


async def test_recipient_declined_share_proposal(mock_view_f: MagicMock, ):
    await view.Collections.recipient_declined_share_proposal(self=mock_view_f.collections, sender_id=1, )
    mock_view_f.collections.shared.user_declined_request_proposal.acow(
        id=1,
        decliner_username=mock_view_f.collections.user.ptb.name
    )


@pytest.mark.parametrize(
    argnames=('is_chosen', 'text',),
    argvalues=((True, Texts.POST_SUCCESS_ADDED_TO_COLLECTION,), (False, Texts.POST_SUCCESS_REMOVED_FROM_COLLECTION),),
)
async def test_update_chosen_collection(
        mock_view_f: MagicMock,
        mock_callback_query: MagicMock,
        is_chosen: bool,
        text: str,
):
    await view.Collections.update_chosen_collection(
        self=mock_view_f.collections,
        collection_name='foo',
        is_chosen=is_chosen,
        tooltip=mock_callback_query,
        keyboard=typing_Any,
    )
    mock_view_f.collections.bot.edit_message_reply_markup.acow(
        chat_id=mock_view_f.collections.id,
        message_id=mock_callback_query.message.message_id,
        reply_markup=typing_Any,
    )
    mock_callback_query.answer.acow(text=text.format(COLLECTION_NAME='foo', ), )


class TestKeyboards:

    class TestShowCollectionPosts:
        test_cls = view.Keyboards.Inline.ShowCollections

        def test_build_cbk_data(self, collection_s: ICollection, ):
            result = self.test_cls.build_callback(collection=collection_s, )
            assert result == f'{view.Cbks.SHOW_COLLECTION_POSTS} 1'

        def test_build_inline_button(self, collection_s: ICollection, ):
            result = self.test_cls.build_inline_button(collection=collection_s, )
            assert result == tg_IKB(
                text=collection_s.name,
                callback_data=self.test_cls.build_callback(collection=collection_s, ),
            )

        def test_extract_cbk_data(self, ):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{view.Cbks.SHOW_COLLECTION_POSTS} 1', )
            assert result == 1

    class TestMarkAndShow:
        test_cls = view.Keyboards.Inline.MarkAndShow

        def test_build_cbk_data(self, collection_s: ICollection, ):
            result = self.test_cls.build_callback(collection=collection_s, )
            assert result == f'{view.Cbks.MARK_COLLECTION_AND_SHOW_POSTS} 1'

        def test_build_inline_button(self, collection_s: ICollection, ):
            result = self.test_cls.build_inline_button(collection=collection_s, )
            assert result == tg_IKB(
                text=collection_s.name,
                callback_data=self.test_cls.build_callback(collection=collection_s, ),
            )

        def test_extract_cbk_data(self):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{view.Cbks.MARK_COLLECTION_AND_SHOW_POSTS} 1', )
            assert result == 1

    class TestShowPostsForRecipient:
        class Attrs:
            test_cls = view.Keyboards.Inline.ShowPostsToRecipient

        test_cls = Attrs.test_cls

        def test_build_cbk_data(self, collection_s: ICollection, ):
            result = self.test_cls.build_callback(collection=collection_s, sender_id=1, )
            assert result == f'{view.Cbks.SHOW_SHARED_COLLECTION_POSTS} {1} {collection_s.id}'

        def test_build_inline_button(self, collection_s: ICollection, ):
            result = self.test_cls.build_inline_button(collection=collection_s, sender_id=1, )
            assert result == tg_IKB(
                text=collection_s.name,
                callback_data=self.test_cls.build_callback(collection=collection_s, sender_id=1, ),
            )

        class TestExtractCbkData(Attrs, ):
            def test_with_user(self, user_s: IUser, ):
                cbk_data = f"{view.Cbks.SHOW_COLLECTION_POSTS} 1 2"
                with patch_object(model.Collection, 'User', ) as mock_user:
                    result = self.test_cls.extract_cbk_data(cbk_data=cbk_data, user=user_s, )
                assert result == (user_s, 2,)
                mock_user.assert_not_called()

            def test_without_user(self, ):
                cbk_data = f"{view.Cbks.SHOW_COLLECTION_POSTS} 1 2"
                with patch_object(model.Collection, 'User', ) as mock_user:
                    result = self.test_cls.extract_cbk_data(cbk_data=cbk_data, )
                assert result == (mock_user.return_value, 2,)
                mock_user.acow(id=1, )

    class TestMark:
        test_cls = view.Keyboards.Inline.Mark

        def test_build_cbk_data(self, collection_s: ICollection, ):
            result = self.test_cls.build_callback(collection=collection_s, )
            assert result == f'{view.Cbks.MARK_COLLECTION} 1'

        def test_build_inline_button(self, collection_s: ICollection, ):
            result = self.test_cls.build_inline_button(collection=collection_s, )
            assert result == tg_IKB(
                text=collection_s.name,
                callback_data=self.test_cls.build_callback(collection=collection_s, ),
            )

        def test_extract_cbk_data(self):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{view.Cbks.MARK_COLLECTION} 1', )
            assert result == 1

    class TestChooseForPost:
        test_cls = view.Keyboards.Inline.ChooseForPost

        def test_build_cbk_data(self, collection_s: ICollection, ):
            result = self.test_cls.build_callback(collection=collection_s, is_chosen=True, )
            assert result == f'{view.Cbks.CHOOSE_COLLECTION} {collection_s.name} 1'
            result = self.test_cls.build_callback(collection=collection_s, is_chosen=False, )
            assert result == f'{view.Cbks.CHOOSE_COLLECTION} {collection_s.name} 0'

        def test_build_inline_button(self, collection_s: ICollection, ):
            # Test selected
            btn = self.test_cls.build_inline_button(collection=collection_s, is_chosen=True, )
            assert isinstance(btn, tg_IKB, )
            assert btn.text == f'{collection_s.name}{self.test_cls.CHECKED_CHECKBOX}'
            assert btn.callback_data == self.test_cls.build_callback(collection=collection_s, is_chosen=True, )
            # Test not selected
            btn = self.test_cls.build_inline_button(collection=collection_s, is_chosen=False, )
            assert isinstance(btn, tg_IKB, )
            assert btn.text == collection_s.name
            assert btn.callback_data == self.test_cls.build_callback(collection=collection_s, is_chosen=False, )

        def test_extract_cbk_data(self, faker: Faker, ):
            for i in range(3):
                name = faker.sentence()
                result = self.test_cls.extract_cbk_data(cbk_data=f'{self.test_cls.PREFIX} {name} 1')
                assert result == (name, 0)

        class TestUpdateKeyboard:
            """test_update_keyboard"""
            test_cls = view.Keyboards.Inline.ChooseForPost

            def test_chosen(self, collection_s: ICollection, ):
                btn_to_ignore = self.test_cls.build_inline_button(collection=collection_s, is_chosen=False, )
                btn_to_update = self.test_cls.build_inline_button(collection=collection_s, is_chosen=True, )
                tg_ikm_keyboard = tg_IKM(inline_keyboard=((btn_to_ignore, btn_to_update,),))
                expected_btn_to_update = tg_IKB(
                    callback_data=f'{view.Cbks.CHOOSE_COLLECTION} {collection_s.name} 0',
                    # CHanged True to False
                    text=collection_s.name,
                )
                updated_keyboard = self.test_cls.update_keyboard(
                    keyboard=tg_ikm_keyboard,
                    btn_cbk_data=btn_to_update.callback_data,
                )
                assert updated_keyboard.inline_keyboard == ((btn_to_ignore, expected_btn_to_update,),)

            def test_not_chosen(self, collection_s: ICollection, ):
                btn_to_ignore = self.test_cls.build_inline_button(collection=collection_s, is_chosen=True, )
                btn_to_update = self.test_cls.build_inline_button(collection=collection_s, is_chosen=False, )
                tg_ikm_keyboard = tg_IKM(inline_keyboard=((btn_to_ignore, btn_to_update,),))
                expected_btn_to_update = tg_IKB(
                    callback_data=f'{view.Cbks.CHOOSE_COLLECTION} {collection_s.name} 1',
                    # CHanged False to True
                    text=f'{collection_s.name}{self.test_cls.CHECKED_CHECKBOX}',
                )
                updated_keyboard = self.test_cls.update_keyboard(
                    keyboard=tg_ikm_keyboard,
                    btn_cbk_data=btn_to_update.callback_data,
                )
                assert updated_keyboard.inline_keyboard == ((btn_to_ignore, expected_btn_to_update,),)
