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

from .constants import Cbks
from .texts import FOR_READY
from ..collection.constants import Cbks as CollectionsCbks  # Just for convenience, may be used separate constants
from ..collection.model import Collection
from ..collection.services import Collection as CollectionService
from ..collection.view import Keyboards
from ..post.model import VotedPost

if TYPE_CHECKING:
    from telegram import Update
    from custom_ptb.callback_context import CallbackContext as CallbackContext


async def start_cmd(_: Update, context: CallbackContext, ):
    """Common entry point for both CHs"""
    await context.view.cjm.start_mode()
    return


async def public_mode_cmd(_: Update, context: CallbackContext, ):
    default_collections = CollectionService.get_defaults(prefix=CollectionService.NamePrefix.PUBLIC, )
    await context.view.cjm.public_mode_show_collections(collections=default_collections, )
    return 0


class PersonalMode:

    class CBK:
        cbk_map = {
            CollectionsCbks.SHOW_COLLECTION_POSTS: Keyboards.Inline.ShowPostsToRecipient.extract_cbk_data,
            Cbks.MARK_COLLECTION_AND_SHOW_POSTS: Keyboards.Inline.MarkAndShow.extract_cbk_data,
        }

        @classmethod
        def extract(cls, cbk_data: str, ) -> int:
            pattern = cbk_data.split()[0]
            extract_func = cls.cbk_map[pattern]
            result = extract_func(cbk_data=cbk_data, )
            return result

    @staticmethod
    async def entry_point(_: Update, context: CallbackContext, ):
        default_collections = CollectionService.get_defaults(prefix=CollectionService.NamePrefix.PERSONAL, )
        collections = default_collections + context.user.get_collections()
        sent_message = await context.view.cjm.personal_mode_show_collections(collections=collections, )
        await context.view.notify_ready_keyword()
        context.user_data.tmp_data.collections_to_share = context.user_data.tmp_data.CollectionsToShare(
            message_id_with_collections=sent_message.message_id,
        )
        return 0

    @classmethod
    async def show_collection_posts_to_sender_cbk_handler(cls, update: Update, context: CallbackContext, ):
        """
        Show collection posts and mark it as shown, the opponent wll get only shown collections.
        Exactly marking and showing to make the process more interactive and alive.
        VotedPost.Personal.from_posts.opposite no need on this stage (?)
        (Just marking exists at all ?)
        """
        collection_id = cls.CBK.extract(cbk_data=update.callback_query.data, )
        context.user_data.tmp_data.collections_to_share.ids.add(collection_id, )
        posts = Collection.get_posts(
            collection_id=collection_id,
            connection=context.connection,
        )
        voted_personal_posts = VotedPost.Personal.from_posts(posts=posts, clicker=context.user, )
        await context.view.collections.show_collection_posts(
            posts=voted_personal_posts,
            tooltip=update.callback_query,
        )
        # Better to add a real message and remove it on collection close
        # but this message id not exists during collection sending
        await update.callback_query.answer(text=FOR_READY, )
