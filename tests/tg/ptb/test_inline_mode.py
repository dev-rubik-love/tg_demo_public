from __future__ import annotations

from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from telegram.constants import MessageType
from telegram import (
    InlineKeyboardMarkup as Ikm,
    InlineKeyboardButton as Ikb,
    InlineQueryResultArticle,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedDocument,
    InputTextMessageContent,
)
from telegram.ext import ApplicationHandlerStop

from app.tg.ptb.structures import InlineData, PostsCategories, InlinePost
from app.tg.ptb import inline_mode

from tests.conftest import patch_object
from tests.tg.ptb.conftest import public_post_s

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.entities.collection.model import ICollection
    from app.tg.ptb.entities.post.model import IPublicPost


@pytest.fixture(scope='function', )
def patched_logger() -> MagicMock:
    with patch_object(target=inline_mode, attribute='logger', ) as result:
        yield result


@pytest.fixture(scope='function', )
def patched_get_effective_message_type():
    with patch_object(
            target=inline_mode,
            attribute='get_effective_message_type',
    ) as mock_get_effective_message_type:
        yield mock_get_effective_message_type


@pytest.fixture(scope='function', )
def inline_data_f(collection_s: ICollection, public_post_s: IPublicPost, ) -> InlineData:
    yield InlineData(collections=[collection_s, ], posts=PostsCategories(), )


class TestGetInlineResult:
    """test_get_inline_result"""

    @staticmethod
    def test_get_inline_result_text(
            mock_public_post: MagicMock,
            patched_get_effective_message_type: MagicMock,
    ):
        patched_get_effective_message_type.return_value = MessageType.TEXT
        mock_public_post.message.text = mock_public_post.message.caption = None
        result = inline_mode.get_inline_result(
            request_id='1',
            post=mock_public_post,
            reply_markup=typing_Any,
        )
        patched_get_effective_message_type.acow(entity=mock_public_post.message, )
        assert result == InlineQueryResultArticle(
            id='1',
            title='title',
            description=None,
            input_message_content=InputTextMessageContent(
                message_text='',
                entities=mock_public_post.message.entities,
            ),
            reply_markup=typing_Any,
        )

    @staticmethod
    def test_get_inline_result_photo(
            mock_public_post: MagicMock,
            patched_get_effective_message_type: MagicMock,
    ):
        patched_get_effective_message_type.return_value = MessageType.PHOTO
        mock_public_post.message.text = mock_public_post.message.caption = None
        result = inline_mode.get_inline_result(
            request_id='1',
            post=mock_public_post,
            reply_markup=typing_Any,
        )
        patched_get_effective_message_type.acow(entity=mock_public_post.message, )
        assert result == InlineQueryResultCachedPhoto(
            id='1',
            photo_file_id=mock_public_post.message.photo[-1].file_id,
            title='title',
            description=None,
            caption=mock_public_post.message.caption,
            reply_markup=typing_Any,
            caption_entities=mock_public_post.message.caption_entities,
            show_caption_above_media=mock_public_post.message.show_caption_above_media,
        )

    @staticmethod
    def test_get_inline_result_video(
            mock_public_post: MagicMock,
            patched_get_effective_message_type: MagicMock,
    ):
        patched_get_effective_message_type.return_value = MessageType.VIDEO
        mock_public_post.message.text = mock_public_post.message.caption = None
        result = inline_mode.get_inline_result(
            request_id='1',
            post=mock_public_post,
            reply_markup=typing_Any,
        )
        patched_get_effective_message_type.acow(entity=mock_public_post.message, )
        assert result == InlineQueryResultCachedVideo(
            id='1',
            video_file_id=mock_public_post.message.video.file_id,
            title='title',
            description=None,
            caption=mock_public_post.message.caption,
            reply_markup=typing_Any,
            caption_entities=mock_public_post.message.caption_entities,
            show_caption_above_media=mock_public_post.message.show_caption_above_media,
        )

    @staticmethod
    def test_get_inline_result_document(
            mock_public_post: MagicMock,
            patched_get_effective_message_type: MagicMock,
    ):
        patched_get_effective_message_type.return_value = MessageType.DOCUMENT
        mock_public_post.message.text = mock_public_post.message.caption = None
        result = inline_mode.get_inline_result(
            request_id='1',
            post=mock_public_post,
            reply_markup=typing_Any,
        )
        patched_get_effective_message_type.acow(entity=mock_public_post.message, )
        assert result == InlineQueryResultCachedDocument(
            id='1',
            document_file_id=mock_public_post.message.document.file_id,
            title='title',
            description=None,
            caption=mock_public_post.message.caption,
            reply_markup=typing_Any,
            caption_entities=mock_public_post.message.caption_entities,
        )


@pytest.mark.parametrize(
    argnames=('category_name', 'message_type'),
    argvalues=(
            ('texts', MessageType.TEXT,),
            ('photos', MessageType.PHOTO,),
            ('videos', MessageType.VIDEO,),
            ('documents', MessageType.DOCUMENT),
    ),
)
def test_add_post_to_inline_data(
        inline_data_f: InlineData,
        public_post_s: IPublicPost,
        patched_get_effective_message_type: MagicMock,
        category_name: str,
        message_type: MessageType,
):
    patched_get_effective_message_type.return_value = message_type
    inline_mode.add_post_to_inline_data(inline_data=inline_data_f, post=public_post_s, )
    assert getattr(inline_data_f.posts, category_name, ) == [InlinePost(post=public_post_s, )]


class TestGetInlinePostKeyboardsVote:
    @staticmethod
    def test_build():
        result = inline_mode.GetInlinePost.Keyboards.Vote.build(post_id=1, )
        assert result == Ikm(
            ((
                 Ikb(
                     text=inline_mode.GetInlinePost.Keyboards.Vote.NEG_EMOJI,
                     callback_data=f'{inline_mode.GetInlinePost.Keyboards.Vote.PREFIX} 1 -1',
                 ),
                 Ikb(
                     text=inline_mode.GetInlinePost.Keyboards.Vote.POS_EMOJI,
                     callback_data=f'{inline_mode.GetInlinePost.Keyboards.Vote.PREFIX} 1 +1',
                 ),
             ),),
        )

    @staticmethod
    @pytest.mark.parametrize(argnames='flag', argvalues=[0, 1])
    def test_extract_cbk_data(flag: bool, ):
        result = inline_mode.GetInlinePost.Keyboards.Vote.extract_cbk_data(
            cbk_data=f'{inline_mode.GetInlinePost.Keyboards.Vote.PREFIX} 1 {flag}',
        )
        assert result == (1, flag)


class TestGetInlinePost:

    @staticmethod
    def test_get_category_inline_results(
            public_post_s: IPublicPost,
            patched_get_effective_message_type: MagicMock,
    ):
        patched_get_effective_message_type.return_value = MessageType.TEXT  # No matter
        result = inline_mode.GetInlinePost.get_category_inline_results(
            unique_id_counter=inline_mode.itertools_count(0),
            category_posts=[InlinePost(post=public_post_s, priority=1, ), ],
        )
        assert result == [
            inline_mode.get_inline_result(
                # A tiny trick to use it like callback data
                request_id=f'ranked_post 0 {public_post_s.id}',
                post=public_post_s,
                description='Популярный пост',
                reply_markup=inline_mode.GetInlinePost.Keyboards.Vote.build(post_id=public_post_s.id, ),
            ),
            inline_mode.get_inline_result(
                # A tiny trick to use it like callback data
                request_id=f'ranked_post 1 {public_post_s.id}',
                post=public_post_s,
                description='Новый пост',
                reply_markup=inline_mode.GetInlinePost.Keyboards.Vote.build(post_id=public_post_s.id, ),
            )
        ]

    @staticmethod
    def test_limit_posts_in_collections(collection_s: ICollection, ):
        with patch_object(
                target=inline_mode,
                attribute='calculate_average_distributions',
                return_value=[1, ],
        ) as mock_calculate_average_distributions:
            result = inline_mode.GetInlinePost.limit_posts_in_collections(limit=1, collections=[collection_s, ], )
        mock_calculate_average_distributions.acow(
            limit=1,
            items=[len(collection.posts) for collection in [collection_s, ]],
        )
        expected = zip([collection_s, ], mock_calculate_average_distributions.return_value, strict=True, )
        assert list(result) == list(expected)  # zip can't be compared directly, need a list

    @staticmethod
    # @pytest.mark.skip(reason='Cache temporary disabled', )
    def test_get_cached_inline_results(inline_data_f: InlineData, patched_get_effective_message_type: MagicMock, ):
        """
        No triggering `get_category_inline_results` cuz categories lists empty but no problem
        cuz `get_category_inline_results` already tested.
        """
        patched_get_effective_message_type.return_value = MessageType.TEXT  # No matter
        collection = inline_data_f.collections[0]
        post = collection.posts[0]
        result = inline_mode.GetInlinePost.get_cached_inline_results(inline_data=inline_data_f, )
        assert result == [inline_mode.get_inline_result(
            request_id=f'0 {post.id}',
            post=post,
            description=f'{collection.name.capitalize()} - стандартная коллекция',
            reply_markup=inline_mode.GetInlinePost.Keyboards.Vote.build(post_id=post.id, ),
        ), ]

    @staticmethod
    async def test_callback(mock_update: MagicMock, mock_context: MagicMock, ):
        with (
            patch_object(
                target=inline_mode.GetInlinePost,
                attribute='get_cached_inline_results',
            ) as mock_get_cached_inline_results,
            pytest.raises(expected_exception=ApplicationHandlerStop, ),
        ):
            await inline_mode.GetInlinePost.callback(update=mock_update, context=mock_context, )
        mock_get_cached_inline_results.acow(inline_data=mock_context.bot_data.inline_data, )
        mock_update.inline_query.answer.acow(
            results=mock_get_cached_inline_results.return_value,
            button=inline_mode.InlineQueryResultsButton(
                text='Поместить сюда свой пост!',
                start_parameter=inline_mode.CREATE_PUBLIC_POST_S,
            ),
            cache_time=10,
            auto_pagination=True,
        )


class TestInlinePostFeedback:
    @staticmethod
    async def test_callback(mock_update: MagicMock, mock_context: MagicMock, public_post_s: IPublicPost, ):
        mock_update.chosen_inline_result.result_id = '_ 1 1'
        inline_post = InlinePost(post=public_post_s, priority=1, )
        mock_context.bot_data.inline_data.posts = PostsCategories(texts=[inline_post, ], )
        with pytest.raises(expected_exception=ApplicationHandlerStop, ):
            await inline_mode.InlinePostFeedback.callback(update=mock_update, context=mock_context, )
        assert inline_post.priority == 2


class TestVoteCbkHandler:
    @staticmethod
    async def test_callback(mock_update: MagicMock, mock_context: MagicMock, ):
        mock_update.callback_query.data = '1 1 1'  # post id and vote value
        handled_vote = mock_context.user.set_vote.return_value
        with (
            pytest.raises(expected_exception=ApplicationHandlerStop, ),
            patch_object(target=inline_mode.ChannelPublicPost, attribute='read', ) as mock_read
        ):
            await inline_mode.VoteCbkHandler.callback(update=mock_update, context=mock_context, )
        mock_read.acow(post_id=1, connection=mock_context.connection, )
        mock_context.user.set_vote.acow(
            post=mock_read.return_value,
            vote=inline_mode.PublicVoteModel(
                user=mock_context.user,
                post_id=1,
                channel_id=0,
                message_id=0,
                value=inline_mode.PublicVoteModel.Value.POSITIVE,
            ),
        )
        mock_update.callback_query.answer(text=inline_mode.get_answer_text(handled_vote=handled_vote, ), )
