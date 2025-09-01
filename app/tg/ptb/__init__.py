from telegram.ext import ExtBot, AIORateLimiter
from app.config import TG_BOT_TOKEN
from telegram.request import HTTPXRequest


def create_bot() -> ExtBot:
    result = ExtBot(
        token=TG_BOT_TOKEN,
        rate_limiter=AIORateLimiter(max_retries=10, ),
        request=HTTPXRequest(connection_pool_size=512, read_timeout=10, write_timeout=10, ),
    )
    return result


bot = create_bot()
