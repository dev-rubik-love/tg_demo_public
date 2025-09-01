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
from string import ascii_lowercase

from app.entities.post.form import PublicPost, PersonalPost

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.entities.post.form import IPersonalPost


class TestPublicPostForm:
    @staticmethod
    def test_create(mock_public_post_form: MagicMock, ):
        PublicPost.create(self=mock_public_post_form, )
        mock_public_post_form.Mapper.Post.create.acow(
            author=mock_public_post_form.author,
            channel_id=mock_public_post_form.channel_id,
            message_id=mock_public_post_form.message_id,
        )


class TestPersonalPostForm:
    @staticmethod
    def test_create(mock_personal_post_form: MagicMock, ):
        mock_personal_post_form.collection_names = ('1',)
        PersonalPost.create(self=mock_personal_post_form, )
        mock_personal_post_form.Mapper.Post.create.acow(
            author=mock_personal_post_form.author,
            channel_id=mock_personal_post_form.channel_id,
            message_id=mock_personal_post_form.message_id,
        )
        mock_personal_post_form.Mapper.Collection.create(
            name='1',
            posts=[mock_personal_post_form.Mapper.Post.create.return_value],
            author=mock_personal_post_form.author,
        )

    @staticmethod
    def test_handle_collection_names(personal_post_form_f: IPersonalPost, ):
        assert PersonalPost.MAX_COLLECTION_NAME_LEN < len(ascii_lowercase)
        expected = {ascii_lowercase[:PersonalPost.MAX_COLLECTION_NAME_LEN], }
        PersonalPost.handle_collection_names(self=personal_post_form_f, text=ascii_lowercase, )
        assert personal_post_form_f.collection_names == expected
        assert all((len(name) <= PersonalPost.MAX_COLLECTION_NAME_LEN for name in expected))

    @staticmethod
    def test_handle_collection_name_btn(personal_post_form_f: IPersonalPost, ):
        PersonalPost.handle_collection_name_btn(self=personal_post_form_f, collection_name='foo', is_chosen=True, )
        assert personal_post_form_f.collection_names == {'foo', }
        assert personal_post_form_f.user_collections_count == 1  # Inaccurate but ok
        PersonalPost.handle_collection_name_btn(self=personal_post_form_f, collection_name='foo', is_chosen=False, )
        assert personal_post_form_f.collection_names == set()
        assert personal_post_form_f.user_collections_count == 0  # Inaccurate but ok
