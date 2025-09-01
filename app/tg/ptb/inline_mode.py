from __future__ import annotations
from typing import TYPE_CHECKING
from logging import getLogger as logging_getLogger
from dataclasses import dataclass
from re import compile as re_compile, sub as re_sub
from heapq import (
    nsmallest as heapq_nsmallest,
    nlargest as heapq_nlargest,
    heapify as heapq_heapify,
    heappush as heapq_heappush,
)
from itertools import count as itertools_count

from telegram.helpers import effective_message_type as get_effective_message_type
from telegram.constants import MessageType
from telegram.constants import InlineQueryLimit
from telegram import (
    # https://docs.python-telegram-bot.org/en/stable/telegram.inputmessagecontent.html#inputmessagecontent
    # Below are child classes of InputMessageContent (except for invoice method)
    InputTextMessageContent,
    InlineQueryResultArticle,
    InlineQueryResultsButton,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedDocument,
    # Keyboards
    InlineKeyboardMarkup as Ikm,
    InlineKeyboardButton as Ikb,
)
from telegram.ext import InlineQueryHandler, ChosenInlineResultHandler, CallbackQueryHandler, ApplicationHandlerStop

from app.config import LOGS_PATH
from app.postconfig import setup_logger
from app.utils import calculate_average_distributions
from app.tg.ptb.structures import InlinePost

from .entities.post.constants import CREATE_PUBLIC_POST_S
from .entities.post.model import ChannelPublicPost

from .entities.vote.model import PublicVote as PublicVoteModel
from .entities.vote.handlers import get_answer_text

if TYPE_CHECKING:
    from telegram import Update, InlineQueryResult
    from rubik_core.entities.vote.base import Value as VoteValue
    from custom_ptb.callback_context import CallbackContext as CallbackContext

    from .structures import InlineData
    from .entities.post.model import IPublicPost
    from .entities.collection.model import ICollection

logger = setup_logger(logger=logging_getLogger(__name__), filename=f'{LOGS_PATH}/{__name__.split(".")[-1]}.log')

URL_R = re_compile(r'http\S+')


def remove_urls(text: str) -> str:
    """No need urls in title"""
    return re_sub(URL_R, '', text)


def get_inline_result(
        request_id: str,
        post: IPublicPost,
        reply_markup: Ikm,
        description: str | None = None,
        *args,
        **kwargs,
) -> InlineQueryResult | None:
    title = remove_urls(text=post.message.text or post.message.caption or '', ).strip()  # No need urls in the titles
    str_message_type = get_effective_message_type(entity=post.message, )
    if str_message_type:
        match MessageType(str_message_type, ):
            case MessageType.TEXT:
                result = InlineQueryResultArticle(
                    id=request_id,
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(  # parse_mode will be auto detected via entities
                        message_text=post.message.text,
                        entities=post.message.entities,
                    ),
                    reply_markup=reply_markup,
                    *args,
                    **kwargs,
                )
                return result
            case MessageType.PHOTO:
                return InlineQueryResultCachedPhoto(
                    id=request_id,
                    photo_file_id=post.message.photo[-1].file_id,
                    title=title,
                    description=description,
                    caption=post.message.caption,
                    reply_markup=reply_markup,
                    caption_entities=post.message.caption_entities,
                    show_caption_above_media=post.message.show_caption_above_media,
                )
            case MessageType.VIDEO:
                return InlineQueryResultCachedVideo(
                    id=request_id,
                    video_file_id=post.message.video.file_id,
                    title=title,
                    description=description,
                    caption=post.message.caption,
                    reply_markup=reply_markup,
                    caption_entities=post.message.caption_entities,
                    show_caption_above_media=post.message.show_caption_above_media,
                )
            case MessageType.DOCUMENT:
                return InlineQueryResultCachedDocument(
                    id=request_id,
                    document_file_id=post.message.document.file_id,
                    title=title,
                    description=description,
                    caption=post.message.caption,
                    reply_markup=reply_markup,
                    caption_entities=post.message.caption_entities,
                )


def add_post_to_inline_data(inline_data: InlineData, post: IPublicPost, ) -> None:
    """Used in post handlers, external usage"""
    str_message_type = get_effective_message_type(entity=post.message, )
    match MessageType(str_message_type, ):
        case MessageType.TEXT:
            heapq_heappush(inline_data.posts.texts, InlinePost(post=post, ))
        case MessageType.PHOTO:
            heapq_heappush(inline_data.posts.photos, InlinePost(post=post, ))
        case MessageType.VIDEO:
            heapq_heappush(inline_data.posts.videos, InlinePost(post=post, ))
        case MessageType.DOCUMENT:
            heapq_heappush(inline_data.posts.documents, InlinePost(post=post, ))
        case _:
            logger.info(msg=f'Unknown message type {str_message_type}')


class GetInlinePost:
    """Provide possible inline results when users types @bot_name"""

    TTL = 300

    @dataclass
    class Keyboards:
        class Vote:
            PREFIX = 'inline_mode_set_vote'
            POS_EMOJI = '👍'
            NEG_EMOJI = '👎'

            @classmethod
            def build(cls, post_id, ) -> Ikm:
                return Ikm.from_row(
                    button_row=(
                        Ikb(text=cls.NEG_EMOJI, callback_data=f'{cls.PREFIX} {post_id} -1', ),
                        Ikb(text=cls.POS_EMOJI, callback_data=f'{cls.PREFIX} {post_id} +1', ),
                    ),
                )

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> tuple[int, VoteValue]:
                _, str_post_id, str_flag = cbk_data.split()
                return int(str_post_id), PublicVoteModel.convert_vote_value(int(str_flag))

    @classmethod
    def limit_posts_in_collections(cls, limit: int, collections: list[ICollection]) -> zip:
        return zip(
            collections,
            calculate_average_distributions(
                limit=limit,
                items=[len(collection.posts) for collection in collections],
            ),
            strict=True,
        )

    @classmethod
    def get_category_inline_results(
            cls,
            unique_id_counter: itertools_count[int],
            category_posts: list[InlinePost],
            popular_posts_num: int = 6,
            new_posts_num: int = 6,
    ):
        """Every category has popular and new posts"""
        results = []
        popular_inline_posts = heapq_nlargest(n=popular_posts_num, iterable=category_posts, )
        new_inline_posts = heapq_nsmallest(n=new_posts_num, iterable=category_posts, )
        for popular_inline_posts in popular_inline_posts:  # _ - priority
            if result := get_inline_result(
                    # A tiny trick to use it like callback data
                    request_id=f'ranked_post {next(unique_id_counter)} {popular_inline_posts.post.id}',
                    post=popular_inline_posts.post,
                    description='Популярный пост',
                    reply_markup=cls.Keyboards.Vote.build(post_id=popular_inline_posts.post.id, ),
            ):
                results.append(result)
        for new_inline_post in new_inline_posts:  # _ - priority
            if result := get_inline_result(
                    # A tiny trick to use it like callback data
                    request_id=f'ranked_post {next(unique_id_counter)} {new_inline_post.post.id}',
                    post=new_inline_post.post,
                    description='Новый пост',
                    reply_markup=cls.Keyboards.Vote.build(post_id=popular_inline_posts.post.id, ),
            ):
                results.append(result)
        return results

    @classmethod
    # @lru_cache(maxsize=5, )  # TODO no cache currently and need to hash the InlineData
    def get_cached_inline_results(cls, inline_data: InlineData, ) -> list[InlineQueryResult]:
        inline_results = []
        popular_posts_num = new_posts_num = 6
        unique_id_counter = itertools_count(0)  # Assign unique key for every item (enumerate will fail on empty list)
        # POSTS
        for category_posts in inline_data.posts:
            inline_results += cls.get_category_inline_results(
                category_posts=category_posts,
                unique_id_counter=unique_id_counter,
            )
        # COLLECTIONS
        limit = InlineQueryLimit.RESULTS - popular_posts_num - new_posts_num
        inline_data.collections = inline_data.collections
        for collection, limit in cls.limit_posts_in_collections(limit=limit, collections=inline_data.collections, ):
            for post in collection.posts[:limit]:
                if result := get_inline_result(
                        request_id=f'{next(unique_id_counter)} {post.id}',
                        post=post,
                        description=f'{collection.name.capitalize()} - стандартная коллекция',
                        reply_markup=cls.Keyboards.Vote.build(post_id=post.id, ),
                ):
                    inline_results.append(result)
        return inline_results

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        inline_results = cls.get_cached_inline_results(inline_data=context.bot_data.inline_data, )
        await update.inline_query.answer(
            results=inline_results,
            button=InlineQueryResultsButton(text='Поместить сюда свой пост!', start_parameter=CREATE_PUBLIC_POST_S, ),
            cache_time=10,
            auto_pagination=True,
        )
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> InlineQueryHandler:
        result = InlineQueryHandler(callback=cls.callback, )
        return result


class InlinePostFeedback:
    """Callback, i.e. post handling. Some additional help stuff on clicked inline result event"""

    CHOSEN_INLINE_PATTERN = re_compile(r'^ranked_post \d+ \d+$')  # priority and post_id

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        _, str_incoming_index, str_post_id = update.chosen_inline_result.result_id.split()
        for category in context.bot_data.inline_data.posts:
            for index, inline_post in enumerate(category, ):  # A tiny trick to use it like callback
                # data
                if inline_post.post.id == int(str_post_id):
                    inline_post.priority += 1
                    heapq_heapify(category)
                    # Compare enumerate results of sending (itertools_count(0)) and receiving stages
                    if int(str_incoming_index) != index:
                        logger.info(
                            msg='incoming index not equals to the found index, '
                                'therefore search loop really required.'
                        )
                    raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> ChosenInlineResultHandler:
        result = ChosenInlineResultHandler(
            callback=cls.callback,
            pattern=cls.CHOSEN_INLINE_PATTERN,
        )
        return result


class VoteCbkHandler:
    """Callback, i.e. post handling. Some additional help stuff on clicked inline result event"""

    PATTERN = re_compile(fr'^{GetInlinePost.Keyboards.Vote.PREFIX} \d+ [+-]?1$')  # [+-]? - optional + or - sign

    @classmethod
    async def callback(cls, update: Update, context: CallbackContext, ):
        """
        Callback may be abused, remember this!
        If user pressed button from forwarded message (default disable):
        https://stackoverflow.com/q/46756643/11277611
        """
        post_id, vote_value = GetInlinePost.Keyboards.Vote.extract_cbk_data(cbk_data=update.callback_query.data, )
        try:
            post = ChannelPublicPost.read(post_id=post_id, connection=context.connection, )
            vote = PublicVoteModel(
                user=context.user,
                post_id=post_id,
                channel_id=0,
                message_id=0,
                value=vote_value,
            )
        except Exception as e:
            logger.error(msg=e, exc_info=True, )
            await context.view.posts.voting_internal_error(tooltip=update.callback_query, )
        else:  # If no exception was raised
            handled_vote = context.user.set_vote(post=post, vote=vote, )
            await update.callback_query.answer(text=get_answer_text(handled_vote=handled_vote, ), )
        raise ApplicationHandlerStop()  # Prevent execution of any other handler (even in different groups)

    @classmethod
    def create_handler(cls, ) -> CallbackQueryHandler:
        result = CallbackQueryHandler(callback=cls.callback, pattern=cls.PATTERN, )
        return result


get_inline_post_handler = GetInlinePost.create_handler()
inline_post_feedback_handler = InlinePostFeedback.create_handler()
vote_handler = VoteCbkHandler.create_handler()

available_handlers = {
    -7: (get_inline_post_handler, inline_post_feedback_handler, vote_handler,),
}
