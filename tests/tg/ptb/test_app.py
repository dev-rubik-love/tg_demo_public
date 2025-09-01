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

from typing import TYPE_CHECKING, Type
from pathlib import PosixPath
from unittest.mock import create_autospec

from pytest import mark as pytest_mark, fixture as pytest_fixture

from app.tg.ptb.entities.post import model as post_model

from app.tg.ptb.entities.mix.handlers import error_handler
from app.tg.ptb.entities.mix.handlers_definition import faq_handler_cmd
from app.tg.ptb.entities.match.handlers_definition import search_ch
from app.tg.ptb import app as ptb_app

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from telegram.ext import ExtBot

COLLECTIONS = {"collection_name": [{"path": PosixPath("path/to/file"), "text": "caption_text"}, ], }


@pytest_fixture(scope='function', )
def patched_create_ptb_app_bone():
    with patch_object(ptb_app, 'create_ptb_app_bone', ) as mock_create_ptb_app_bone:
        yield mock_create_ptb_app_bone


def test_mock_create_ptb_app_bone(ptb_bot_s: ExtBot, ):
    """Nothing to test here"""
    ptb_app.create_ptb_app_bone(bot=ptb_bot_s, )


class TestCreatePtbApp:
    @staticmethod
    @pytest_mark.parametrize(
        argnames='mock_handlers',
        argvalues=(  # Multiple different types of handler
                create_autospec(spec=search_ch, spec_set=True, ),
                create_autospec(spec=faq_handler_cmd, spec_set=True, ),
        ), )
    def test_handlers_passed(patched_create_ptb_app_bone: MagicMock, mock_bot: MagicMock, mock_handlers: MagicMock, ):
        mock_error_handler = create_autospec(spec=error_handler, spec_set=True, )
        result = ptb_app.create_ptb_app(
            bot=mock_bot,
            handlers=mock_handlers,
            error_handler=mock_error_handler,
        )
        patched_create_ptb_app_bone.return_value.add_handlers.acow(handlers=mock_handlers, )
        patched_create_ptb_app_bone.return_value.add_error_handler.acow(callback=mock_error_handler, block=False, )
        assert result == patched_create_ptb_app_bone.return_value

    @staticmethod
    def test_handlers_not_passed(patched_create_ptb_app_bone: MagicMock, mock_bot: MagicMock, ):
        result = ptb_app.create_ptb_app(bot=mock_bot, )
        patched_create_ptb_app_bone.return_value.add_handlers.assert_called()  # Many calls
        patched_create_ptb_app_bone.return_value.add_error_handler.assert_called()  # Many calls
        assert result == patched_create_ptb_app_bone.return_value


@pytest_mark.skip(reason='deprecated')
@pytest_mark.parametrize(
    argnames='post_cls, create_public, create_personal, collections',
    argvalues=(
        # (post.PublicPost, True, False, ptb_app.PUBLIC_COLLECTIONS),
        # (post.PersonalPost, False, True, ptb_app.PERSONAL_COLLECTIONS,),
    ), )
def test_configure_app(
        mock_bot: MagicMock,
        post_cls: Type,
        create_public: bool,
        create_personal: bool,
        collections: dict[str, [{str, PosixPath}]]
):
    with (
        patch_object(target=ptb_app.db_manager.Postgres, attribute='create_app_tables', ) as mock_create_app_tables,
        patch_object(target=post_model, attribute=post_cls.__name__, ) as mock_post_cls,
        patch_object(
            target=ptb_app,
            attribute='create_default_collections_with_posts',
        ) as mock_create_default_collections_with_posts,
    ):
        ptb_app.configure_app(
            bot=mock_bot,
            create_public_default_collections=create_public,
            create_personal_default_collections=create_personal,
        )
    mock_create_app_tables.acow()
    mock_create_default_collections_with_posts.acow(bot=mock_bot, collections=collections, post_cls=mock_post_cls, )
