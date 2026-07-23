from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.models.user import get_user_by_tgid

class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Aiogram автоматично додає об'єкт користувача Telegram у data["event_from_user"]
        tg_user = data.get("event_from_user")
        
        if tg_user:
            # Робимо запит до твоєї бази
            user_db = await get_user_by_tgid(tg_user.id)
            
            # Якщо користувач є в базі, прокидаємо його у хендлери під ключем "user"
            # (Якщо у тебе є логіка реєстрації, тут можна додати створення юзера, якщо він None)
            data["user"] = user_db

        # Передаємо управління далі (наступним мідлварям або самому хендлеру)
        return await handler(event, data)