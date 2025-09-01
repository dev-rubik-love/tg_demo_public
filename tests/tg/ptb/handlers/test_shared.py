from __future__ import annotations
from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from app.tg.ptb.entities.shared import handlers

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock


async def test_unclickable_cbk_handler(mock_update: MagicMock, mock_context: MagicMock, ):
    await handlers.unclickable_cbk_handler(update=mock_update, context=mock_context, )
    mock_context.view.unclickable_button.acow(tooltip=mock_update.callback_query, )


async def test_cancel(mock_context: MagicMock, ):
    await handlers.cancel(_=typing_Any, context=mock_context, )
    mock_context.view.cancel.acow()


class TestShowProfileCbkHandler:
    """test_show_profile_cbk_handler"""

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_user_cls(mock_user: MagicMock, ):
        with patch_object(target=handlers, attribute='User', return_value=mock_user, ) as result:
            yield result

    @staticmethod
    async def test_registered(mock_update: MagicMock, mock_context: MagicMock, patched_user_cls: MagicMock, ):
        mock_profile_cls = mock_context.view.match.Profile
        mock_profile = mock_profile_cls.return_value
        mock_update.callback_query.data = '_ 1'  # user_id
        mock_user = patched_user_cls.return_value
        await handlers.show_profile_cbk_handler(update=mock_update, context=mock_context, )
        patched_user_cls.acow(id=1, )
        mock_profile_cls.acow(bot=mock_context.bot, data_source=mock_user, id=1)
        mock_profile.send.acow(show_to_id=mock_update.callback_query.from_user.id, )
        mock_user.load.acow()
        mock_update.callback_query.answer.acow()

    @staticmethod
    async def test_not_registered(mock_update: MagicMock, mock_context: MagicMock, patched_user_cls: MagicMock, ):
        mock_update.callback_query.data = '_ 1'  # user_id
        patched_user_cls.return_value.is_registered = False
        await handlers.show_profile_cbk_handler(update=mock_update, context=mock_context, )
        patched_user_cls.acow(id=1, )
        patched_user_cls.return_value.load.acow()
        mock_update.callback_query.answer.acow(
            text=handlers.texts.USER_NOT_REGISTERED,
            show_alert=True,
        )

