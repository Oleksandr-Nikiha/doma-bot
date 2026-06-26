import json

from bot.services.database import db
from bot.services.cache import cache
from bot.config import settings

async def get_message(handler: str, key: str, **kwargs) -> str:
    cache_key = f"msg:{handler}"
    messages = None

    if settings.USE_CACHE:
        cached = await cache.get(cache_key)
        if cached:
            messages = json.loads(cached)

    if messages is None:
        row = await db.fetchrow(
            "SELECT messages FROM bot_messages WHERE handler = $1",
            handler,
        )
        if not row:
            return f"[{handler}.{key}]"

        messages = json.loads(row["messages"])

        if settings.USE_CACHE:
            await cache.set(cache_key, json.dumps(messages, ensure_ascii=False), expire=3600)

    text = messages.get(key, f"[{handler}.{key}]")

    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text