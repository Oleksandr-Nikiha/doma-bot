import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from bot.config import settings
from bot.services.database import db
from bot.services.cache import cache

from bot.handlers.common import router as common_router
from bot.handlers.registration import router as registration_router
from bot.handlers.order import router as order_router
from bot.handlers.cart import router as cart_router
from bot.handlers.checkout import router as checkout_router

from bot.handlers.debug import router as debug_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    await db.connect()
    await cache.connect()
    logger.info("Connected to PostgreSQL and Redis")


async def on_shutdown(bot: Bot):
    await db.disconnect()
    await cache.disconnect()
    logger.info("Disconnected from PostgreSQL and Redis")


async def main():
    storage = RedisStorage.from_url(settings.redis_url)

    bot = Bot(
        token=settings.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode='HTML')
    )
    
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_routers(
        common_router, 
        registration_router,
        order_router,
        cart_router,
        checkout_router
    )

    dp.include_router(debug_router)

    logger.info("Bot is starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())