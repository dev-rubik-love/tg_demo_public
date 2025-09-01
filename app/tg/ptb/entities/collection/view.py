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
from typing import TYPE_CHECKING, Iterable, Type
from abc import ABC, abstractmethod

from telegram.constants import ParseMode
from telegram import InlineKeyboardButton as tg_IKB, InlineKeyboardMarkup as tg_IKM, ReplyKeyboardMarkup as tg_RKM

from app.tg.ptb.structures import IKeyboard as IStructuresKeyboard
from app.tg.ptb.custom import CustomInlineKeyboardMarkup

from .constants import Cbks
from .texts import Collections as Texts
from .model import Collection as CollectionModel
from ..shared.texts import Words as SharedWords
from ..post import model as post_model  # For isinstance check
from ..shared.view import SharedInit, Shared as SharedView, Keyboards as SharedKeyboards
from ..post.view import Posts as PostsView, Keyboards as PostsKeyboards

if TYPE_CHECKING:
    from telegram import Message, CallbackQuery
    from .model import ICollection
    from ..user.model import IUser


class Keyboards:
    skip_cancel = tg_RKM(**SharedKeyboards.skip_cancel.to_dict(), is_persistent=True, )
    collections_to_share_not_chosen = SharedKeyboards.finish_cancel
    show_chosen_collections_for_post = SharedKeyboards.finish_cancel
    create_personal_post = PostsKeyboards.create_personal_post
    request_user = SharedKeyboards.request_user

    class Inline:

        class ShowCollections(IStructuresKeyboard, ):
            """For collections recipient"""

            @staticmethod
            def build_callback(collection: ICollection, ) -> str:
                return f'{Cbks.SHOW_COLLECTION_POSTS} {collection.id}'

            @classmethod
            def build_inline_button(cls, collection: ICollection, ) -> tg_IKB:
                cbk_data = cls.build_callback(collection=collection, )
                btn = tg_IKB(text=collection.name, callback_data=cbk_data, )
                return btn

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

        class MarkAndShow(IStructuresKeyboard, ):
            """For collections recipient"""

            @staticmethod
            def build_callback(collection: ICollection, ) -> str:
                return f'{Cbks.MARK_COLLECTION_AND_SHOW_POSTS} {collection.id}'

            @classmethod
            def build_inline_button(cls, collection: ICollection, ) -> tg_IKB:
                cbk_data = cls.build_callback(collection=collection, )
                btn = tg_IKB(text=collection.name, callback_data=cbk_data, )
                return btn

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

        class ShowPostsToRecipient(IStructuresKeyboard, ):
            """Personal mode. For recipient collections directly via personal mode"""

            @staticmethod
            def build_callback(collection: ICollection, sender_id: int, ) -> str:
                return f'{Cbks.SHOW_SHARED_COLLECTION_POSTS} {sender_id} {collection.id}'

            @classmethod
            def build_inline_button(cls, collection: ICollection, sender_id: int, ) -> tg_IKB:
                cbk_data = cls.build_callback(collection=collection, sender_id=sender_id, )
                btn = tg_IKB(text=collection.name, callback_data=cbk_data, )
                return btn

            @staticmethod
            def extract_cbk_data(
                    cbk_data: str,
                    user: IUser | None = None,
            ) -> tuple[IUser, int]:
                _, str_sender_id, str_collection_id = cbk_data.split()
                sender_id = int(str_sender_id)
                if user is not None and user.id == sender_id:
                    sender = user
                else:
                    sender = CollectionModel.User(id=sender_id, )
                return sender, int(str_collection_id)

        class Mark(IStructuresKeyboard, ):
            """For user sharing collections directly or via personal mode"""

            @staticmethod
            def build_callback(collection: ICollection, ) -> str:
                return f'{Cbks.MARK_COLLECTION} {collection.id}'

            @classmethod
            def build_inline_button(cls, collection: ICollection, ) -> tg_IKB:
                cbk_data = cls.build_callback(collection=collection, )
                btn = tg_IKB(text=collection.name, callback_data=cbk_data, )
                return btn

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

        class ChooseForPost(IStructuresKeyboard, ):
            """For choosing collections for post during post creation"""

            CHECKED_CHECKBOX = '☑'
            PATTERN = Cbks.CHOOSE_COLLECTION_R
            PREFIX = Cbks.CHOOSE_COLLECTION

            @classmethod
            def build_callback(cls, collection: ICollection, is_chosen: bool, ) -> str:
                return f'{cls.PREFIX} {collection.name} {int(is_chosen)}'

            @classmethod
            def build_inline_button(cls, collection: ICollection, is_chosen: bool = False, ) -> tg_IKB:
                cbk_data = cls.build_callback(collection=collection, is_chosen=is_chosen, )
                checkbox = cls.CHECKED_CHECKBOX if is_chosen else ''
                btn = tg_IKB(text=f'{collection.name}{checkbox}', callback_data=cbk_data, )
                return btn

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> tuple[str, bool]:
                """
                *collection_name - collection may contain spaces, this will collect all parts of the name to tuple
                " ".join - convert names tuple  back to string
                not bool - for inversion (is this a right place?)
                """
                _, *arbitrary_collection_name, is_chosen = cbk_data.split()
                return ' '.join(arbitrary_collection_name), not bool(int(is_chosen))  # See docstring

            @classmethod
            def update_keyboard(cls, btn_cbk_data, keyboard: tg_IKM, ) -> tg_IKM:
                """
                returns new keyboard cuz tg_IKM keyboard immutable in PTB.
                is_chosen param no need cuz current value from keyboard just will be negated
                """
                btn, row_index, column_index = CustomInlineKeyboardMarkup.find_btn_by_cbk(
                    inline_keyboard=keyboard.inline_keyboard,
                    cbk=btn_cbk_data,
                )
                if btn.callback_data[-1] == '0':  # invert old value
                    new_cbk_data = f'{btn.callback_data[:-1]}1'
                    new_text = f'{btn.text}{cls.CHECKED_CHECKBOX}'
                else:  # if 1
                    new_cbk_data = f'{btn.callback_data[:-1]}0'
                    new_text = btn.text[:-1]  # [:-1] - remove checkbox, it's only for chosen
                new_inline_keyboard = [list(row) for row in keyboard.inline_keyboard]
                new_inline_keyboard[row_index][column_index] = tg_IKB(text=new_text, callback_data=new_cbk_data)
                return tg_IKM(inline_keyboard=new_inline_keyboard, )


class ICollections(ABC, ):

    @abstractmethod
    async def no_collections(self) -> Message:
        ...

    @abstractmethod
    async def propose_collections_for_post(self, collections: list[ICollection]) -> None:
        ...

    @abstractmethod
    async def collections_to_share_not_chosen(self, reply_to_message_id: int, ) -> Message:
        ...

    @abstractmethod
    async def show_chosen_collections_for_post(self, collection_names: set[str]) -> Message:
        ...

    @abstractmethod
    async def ask_collections(self) -> Message:
        ...

    @abstractmethod
    async def ask_who_to_share(self) -> Message:
        ...

    @abstractmethod
    async def recipient_declined_share_proposal(self, sender_id: int) -> Message:
        ...

    @abstractmethod
    async def recipient_accepted_share_proposal(self, sender_id: int) -> Message:
        ...

    @abstractmethod
    async def show_collection_posts(
            self,
            posts: list[post_model.IVotedPublicPost | post_model.IVotedPersonalPost],
            tooltip: CallbackQuery
    ) -> None:
        ...

    @abstractmethod
    async def no_posts_in_collection(self, tooltip: CallbackQuery) -> bool:
        ...

    @abstractmethod
    async def here_collection_posts(self) -> Message:
        ...

    @abstractmethod
    async def posts_not_found(self, tooltip: CallbackQuery) -> bool:
        ...

    @abstractmethod
    async def few_posts_not_found(self, num: int, tooltip: CallbackQuery) -> bool:
        ...

    @abstractmethod
    async def ask_accept_collections(self, recipient_id: int, collections_ids: set[int]) -> Message:
        ...

    @abstractmethod
    async def show_collections(
            self,
            collections: list['ICollection'],
            text: str,
            keyboard: Type[IStructuresKeyboard],
    ) -> Message:
        ...

    @abstractmethod
    async def show_shared_collections(self, collections: list['ICollection'], sender_id: int) -> Message:
        ...

    @abstractmethod
    async def show_my_collections(self, collections: list['ICollection']) -> Message:
        ...

    @abstractmethod
    async def shared_collections_not_found(self) -> Message:
        ...


class Collections(ICollections, SharedInit, ):
    def __init__(self, user: IUser, posts_view: PostsView, shared_view: SharedView, ):
        super().__init__(user=user, )
        self.posts_view = posts_view
        self.shared = shared_view

    async def no_collections(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.NO_COLLECTIONS,
            reply_markup=Keyboards.create_personal_post,
        )

    async def propose_collections_for_post(self, collections: list[ICollection], ) -> None:
        """Should be 2 messages to provide both keyboards, reply and inline (TG restriction)"""
        await self.bot.send_message(
            chat_id=self.id,
            text=Texts.ASK_FOR_NAMES,
            reply_markup=SharedKeyboards.cancel_factory(
                buttons=(SharedWords.READY,),
                one_time_keyboard=False,  # Keep keyboard otherwise it will be hidden when user start typing
            ), )
        if collections:
            await self.show_collections(
                collections=collections,
                text=Texts.HERE_YOUR_COLLECTIONS,
                keyboard=Keyboards.Inline.ChooseForPost,
            )
        # Feature say user have no collections currently

    async def collections_to_share_not_chosen(self, reply_to_message_id: int, ) -> Message:
        return await self.bot.send_message(
            text=Texts.COLLECTIONS_TO_SHARE_NOT_CHOSE,
            chat_id=self.id,
            reply_markup=Keyboards.collections_to_share_not_chosen,
            reply_to_message_id=reply_to_message_id,
        )

    async def show_chosen_collections_for_post(self, collection_names: set[str], ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=(
                f'{Texts.SAY_CHOSE_FOR_POST}\n'
                # Note: A pair of tags outside of join
                f'<code><i>{"</i></code>, <code><i>".join(collection_names)}</i></code>.'),
            reply_markup=Keyboards.show_chosen_collections_for_post,
            parse_mode=ParseMode.HTML,
        )

    async def ask_collections(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.ASK_TO_SHARE,
            reply_markup=Keyboards.skip_cancel,

        )

    async def ask_who_to_share(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.WHO_TO_SHARE,
            reply_markup=Keyboards.request_user(),
        )

    async def recipient_declined_share_proposal(self, sender_id: int, ) -> Message:
        return await self.shared.user_declined_request_proposal(
            id=sender_id,
            decliner_username=self.user.ptb.name,
        )

    async def recipient_accepted_share_proposal(self, sender_id: int, ) -> Message:
        return await self.bot.send_message(
            chat_id=sender_id,
            text=Texts.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_USERNAME=self.user.ptb.name, ),
        )

    async def show_collection_posts(
            self,
            posts: list[post_model.IVotedPublicPost | post_model.IVotedPersonalPost],
            tooltip: CallbackQuery,
    ) -> None:
        if not posts:
            await self.no_posts_in_collection(tooltip=tooltip, )  # TODO raise and remove btn
            return None
        elif await self.check_collection_posts_existence(posts=posts, ) is False:
            await self.posts_not_found(tooltip=tooltip, )
            return None
        welcome_message = await self.here_collection_posts()
        sent_messages = await self.posts_view.show_posts(posts=posts, )
        if not sent_messages:  # Post check if checked state suddenly changed during sending
            await self.posts_not_found(tooltip=tooltip, )  # Delete button with this collection?
            return None
        # If suddenly checked state changed during sending
        elif missed_posts_num := (len(posts) > len(sent_messages)):
            await self.few_posts_not_found(num=missed_posts_num, tooltip=tooltip, )
            return None
        if isinstance(posts[-1], post_model.VotedPublicPost):
            keyboard = self.posts_view.public.get_keyboard(
                post=posts[-1].post,
                clicker_vote=posts[-1].clicker_vote,
            )
        else:
            keyboard = self.posts_view.personal.get_keyboard(
                post=posts[-1].post,
                clicker_vote=posts[-1].clicker_vote,
                opposite_vote=posts[-1].opposite_vote,
            )
        await self.shared.add_close_btn(  # Note: can't be added before sending cuz message ids to close are not known
            keyboard=keyboard,
            message_ids_to_close=[welcome_message, *sent_messages],
        )

    async def no_posts_in_collection(self, tooltip: CallbackQuery, ) -> bool:
        return await tooltip.answer(text=Texts.NO_POSTS, show_alert=True, )

    async def here_collection_posts(self, ) -> Message:
        return await self.bot.send_message(chat_id=self.id, text=Texts.HERE_POSTS, )

    async def posts_not_found(self, tooltip: CallbackQuery, ) -> bool:
        return await tooltip.answer(text=Texts.COLLECTION_POSTS_NOT_FOUND, show_alert=True, )

    async def few_posts_not_found(self, num: int, tooltip: CallbackQuery, ) -> bool:
        return await tooltip.answer(
            text=Texts.FEW_POSTS_NOT_FOUND.format(NUM=num),
            show_alert=True,
        )

    async def check_collection_posts_existence(
            self,
            posts: Iterable[post_model.IVotedPublicPost | post_model.IVotedPersonalPost],
    ) -> bool:
        for post in posts:
            if await self.posts_view.check_post_existence(post=post.post, ):
                return True
        return False

    async def ask_accept_collections(self, recipient_id: int, collections_ids: set[int]) -> Message:
        """Proposal to share (send) a collections to someone"""
        return await self.bot.send_message(
            chat_id=recipient_id,  # Add button to show profile if registered instead of fullname
            text=Texts.NOTIFY_SHARE_PROPOSAL.format(USERNAME=self.user.ptb.name, COUNT=len(collections_ids), ),
            reply_markup=tg_IKM(
                ((
                     tg_IKB(
                         text=Texts.Buttons.DECLINE,
                         callback_data=f'{Cbks.ACCEPT_COLLECTIONS} {self.id} 0',
                     ),
                     tg_IKB(
                         text=Texts.Buttons.ACCEPT,
                         callback_data=(
                             f'{Cbks.ACCEPT_COLLECTIONS} '
                             f'{self.id} '
                             f'1 '  # Flag
                             f'{" ".join([str(collection_id) for collection_id in collections_ids])}'
                         ), ),
                 ),
                 (SharedKeyboards.get_show_profile_btn(user_id=self.id, ),),)  # Another row
            ),
        )

    async def show_collections(
            self,
            collections: list[ICollection],
            text: str,
            keyboard: Type[IStructuresKeyboard],
            posts_in_row: int = 2,
    ) -> Message:
        inline_keyboard = CustomInlineKeyboardMarkup.split(
            buttons=[keyboard.build_inline_button(collection=collection, ) for collection in collections],
            btns_in_row=posts_in_row,
        )
        sent_message = await self.bot.send_message(
            text=text,
            chat_id=self.id,
            reply_markup=tg_IKM(inline_keyboard=inline_keyboard, )
        )
        return sent_message

    async def show_shared_collections(
            self,
            collections: list[ICollection],
            sender_id: int,  # In case of sharing collections
    ) -> Message:
        inline_keyboard = CustomInlineKeyboardMarkup.split(
            inline_keyboard=[[Keyboards.Inline.ShowPostsToRecipient.build_inline_button(
                collection=collection,
                sender_id=sender_id,
            ) for collection in collections]],
            btns_in_row=2,
        )
        return await self.bot.send_message(
            text=Texts.HERE_SHARED,
            chat_id=self.id,
            reply_markup=tg_IKM(inline_keyboard=inline_keyboard, ),
        )

    async def show_my_collections(self, collections: list[ICollection], ) -> Message:
        # False positive mypy warning, it's considering passed keyboard as abstract and not concrete implementation
        return await self.show_collections(
            collections=collections,
            text=Texts.HERE_YOUR_COLLECTIONS,
            keyboard=Keyboards.Inline.ShowCollections,
        )

    async def shared_collections_not_found(self, ) -> Message:
        return await self.bot.send_message(
            chat_id=self.id,
            text=Texts.SHARED_COLLECTIONS_NOT_FOUND,
        )

    async def update_chosen_collection(
            self,
            collection_name: str,
            is_chosen: bool,
            tooltip: CallbackQuery,
            keyboard: tg_IKM,
    ) -> None:
        await self.bot.edit_message_reply_markup(
            chat_id=self.id,
            message_id=tooltip.message.message_id,
            reply_markup=keyboard,
        )
        if is_chosen:
            # Note: No need to rename SUCCESS_ADDED -> WILL_BE_ADDED, it's inaccurate but sounds good
            text = Texts.POST_SUCCESS_ADDED_TO_COLLECTION.format(COLLECTION_NAME=collection_name, )
        else:
            text = Texts.POST_SUCCESS_REMOVED_FROM_COLLECTION.format(COLLECTION_NAME=collection_name, )
        await tooltip.answer(text=text, )
