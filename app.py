from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.database.db import Database
from bot.handlers.admin import router as admin_router
from bot.handlers.errors import router as errors_router
from bot.handlers.user import router as user_router
from config import load_config


async def main() -> None:
    config = load_config()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    db = Database(config.db_path)
    await db.init()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(errors_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, db=db, admin_id=config.admin_id)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
