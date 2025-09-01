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

from unittest.mock import patch, create_autospec
from typing import TYPE_CHECKING, Any as typing_Any, Callable

import pytest

from app.tg.ptb.entities.cjm import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from telegram import Update
    from unittest.mock import MagicMock
    from app.tg.ptb.entities.post.model import IPersonalPost


async def test_start_cmd(mock_context: MagicMock):
    await handlers.start_cmd(_=typing_Any, context=mock_context)
    mock_context.view.cjm.start_mode.acow()


async def test_public_mode_cmd(mock_context: MagicMock, mock_update: Update, ):
    with patch_object(target=handlers.CollectionService, attribute='get_defaults', ) as mock_get_defaults:
        result = await handlers.public_mode_cmd(_=typing_Any, context=mock_context, )
    mock_get_defaults.acow(prefix=handlers.CollectionService.NamePrefix.PUBLIC.value, )
    mock_context.view.cjm.public_mode_show_collections.acow(
        collections=mock_get_defaults.return_value,
    )
    assert result == 0


class TestPersonalMode:
    """test_personal_mode"""

    @staticmethod
    @pytest.mark.parametrize(argnames=('pattern', 'func',), argvalues=handlers.PersonalMode.CBK.cbk_map.items(), )
    def test_extract(mock_callback_query: MagicMock, pattern: str, func: Callable, ):
        with patch.dict(  # Patching object a bit hard cuz it's bound classmethod
                in_dict=handlers.PersonalMode.CBK.cbk_map,
                values={pattern: create_autospec(spec=func, spec_set=True, )},
        ) as mock_cbk_map:
            cbk_data = f'{pattern} 1'
            result = handlers.PersonalMode.CBK.extract(cbk_data=cbk_data, )
            mock_cbk_map[pattern].acow(cbk_data=cbk_data)
            assert result == mock_cbk_map[pattern].return_value

    @staticmethod
    async def test_entry_point(mock_context: MagicMock, patched_ptb_collection: MagicMock, ):
        with patch_object(target=handlers.CollectionService, attribute='get_defaults', ) as mock_get_defaults:
            result = await handlers.PersonalMode.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_get_defaults.acow(
            prefix=handlers.CollectionService.NamePrefix.PERSONAL.value,
        )
        mock_context.user.get_collections.acow()
        mock_context.view.notify_ready_keyword.assert_called_with()
        mock_context.view.cjm.personal_mode_show_collections.assert_called_with(
            collections=(
                    mock_get_defaults.return_value +
                    mock_context.user.get_collections.return_value
            ),
        )
        assert result == 0

    @staticmethod
    async def test_test_mark_show_cbk_handler(
            mock_update: MagicMock,
            mock_context: MagicMock,
            personal_post_s: IPersonalPost,
    ):
        assert mock_context.user_data.tmp_data.collections_to_share.ids == set()
        with (
            patch_object(target=handlers.PersonalMode.CBK, attribute='extract', ) as mock_extract,
            patch_object(
                target=handlers.Collection,
                attribute='get_posts',
                return_value=[personal_post_s, ],
            ) as mock_get_posts,
        ):
            await handlers.PersonalMode.show_collection_posts_to_sender_cbk_handler(
                update=mock_update,
                context=mock_context,
            )
        assert mock_context.user_data.tmp_data.collections_to_share.ids == {mock_extract.return_value, }
        mock_extract.acow(cbk_data=mock_update.callback_query.data, )
        mock_get_posts.acow(
            collection_id=mock_extract.return_value,
            connection=mock_context.connection,
        )
        mock_context.view.collections.show_collection_posts.acow(
            tooltip=mock_update.callback_query,
            posts=handlers.VotedPost.from_posts(
                posts=mock_get_posts.return_value,
                clicker=mock_context.user,
            )
        )
        mock_update.callback_query.answer.acow(text=handlers.FOR_READY, )
