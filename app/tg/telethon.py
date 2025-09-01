from __future__ import annotations
from typing import TYPE_CHECKING

from telethon import TelegramClient

from app.config import API_ID, API_HASH, TG_BOT_TOKEN, TELETHON_AUTH_CACHE_PATH
from app.postconfig import telethon_logger as logger

if TYPE_CHECKING:
    from telethon.tl.types import User

client = TelegramClient(TELETHON_AUTH_CACHE_PATH, API_ID, API_HASH)


async def initialize_client() -> None:
    await client.start(bot_token=TG_BOT_TOKEN, )


async def shutdown_client() -> None:
    await client.disconnect()


async def username_to_user(username: str, raise_: bool = True, ) -> User:
    try:
        return await client.get_entity(entity=username, )
    except ValueError as e:  # If the entity can’t be found, ValueError will be raised. (docs).
        if raise_:
            raise e
        else:
            return 0
    except Exception as e:
        logger.error(msg=e, exc_info=True, )
