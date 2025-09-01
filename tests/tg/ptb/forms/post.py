from __future__ import annotations

from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from app.tg.ptb.entities.post import forms

from tests.conftest import patch_object

if TYPE_CHECKING:
    from app.tg.ptb.entities.user.model import IUser
    from app.tg.ptb.entities.post.forms import IPublic as IPublicPostForm


@pytest.fixture(scope='session', )
def public_post_form_s(user_s: IUser, ) -> IPublicPostForm:
    result = forms.Public(author=user_s, channel_id=2, message_id=2, )
    yield result


class TestPublicPost:
    @staticmethod
    def test_create(public_post_form_s: IPublicPostForm, ):
        with patch_object(public_post_form_s.Mapper.Post, 'create', ) as mock_create:
            assert mock_create.return_value.message != public_post_form_s.message
            result = forms.Public.create(self=public_post_form_s, )
        mock_create.acow(
            author=public_post_form_s.author,
            channel_id=public_post_form_s.channel_id,
            message_id=public_post_form_s.message_id,
        )
        assert mock_create.return_value.message == public_post_form_s.message
        assert result == mock_create.return_value
