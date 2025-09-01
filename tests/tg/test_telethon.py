from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, ANY

import pytest

from app.config import TG_BOT_TOKEN
from app.tg import telethon

from tests.conftest import patch_object

if TYPE_CHECKING:
    from unittest.mock import MagicMock


async def test_initialize_client():
    with patch_object(
            target=telethon.client,
            attribute='start',
            new_callable=AsyncMock,  # By some reason autospec failed for async, so used this directly
    ) as mock_start:
        await telethon.initialize_client()
    mock_start.acow(bot_token=TG_BOT_TOKEN, )


async def test_shutdown_client():
    with patch_object(
            target=telethon.client,
            attribute='disconnect',
            new_callable=AsyncMock,  # By some reason autospec failed for async, so used this directly
    ) as mock_disconnect:
        await telethon.shutdown_client()
    mock_disconnect.acow()


class TestUsernameToUser:
    """test_username_to_user"""

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_get_entity():
        with patch_object(target=telethon.client, attribute='get_entity', ) as mock_get_entity:
            yield mock_get_entity

    @staticmethod
    async def test_success(patched_get_entity: MagicMock, ):
        result = await telethon.username_to_user(username='foo', )
        patched_get_entity.acow(entity='foo', )
        assert result == patched_get_entity.return_value

    @staticmethod
    async def test_raise_parameter_true(patched_get_entity: MagicMock, ):
        patched_get_entity.side_effect = ValueError
        with pytest.raises(expected_exception=ValueError, ):
            await telethon.username_to_user(username='foo', raise_=True, )
        patched_get_entity.acow(entity='foo', )

    @staticmethod
    async def test_raise_parameter_false(patched_get_entity: MagicMock, ):
        patched_get_entity.side_effect = ValueError
        result = await telethon.username_to_user(username='foo', raise_=False, )
        patched_get_entity.acow(entity='foo', )
        assert result == 0

    @staticmethod
    async def test_exception(patched_get_entity: MagicMock, ):
        patched_get_entity.side_effect = Exception
        with patch_object(target=telethon, attribute='logger', ) as mock_logger:
            await telethon.username_to_user(username='foo', )
        patched_get_entity.acow(entity='foo', )
        mock_logger.error.acow(msg=ANY, exc_info=True, )
