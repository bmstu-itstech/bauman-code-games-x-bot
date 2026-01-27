from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import settings
from bot.db.pool import create_pool, close_pool
from bot.db.fsm_storage import PgFSMStorage
from bot.middlewares import DbMiddleware, FSMResetMiddleware, register_valid_states
from bot.handlers import start, registration, menu, team_create, team_join, team_info, team_leave


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.DEBUG),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    await create_pool()
    storage = PgFSMStorage()
    bot = Bot(token=settings.telegram_token)
    dp = Dispatcher(storage=storage)

    register_valid_states()

    dp.message.middleware(FSMResetMiddleware())
    dp.callback_query.middleware(FSMResetMiddleware())
    dp.message.middleware(DbMiddleware())
    dp.callback_query.middleware(DbMiddleware())

    dp.include_routers(
        start.router,
        registration.router,
        menu.router,
        team_create.router,
        team_join.router,
        team_info.router,
        team_leave.router,
    )

    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
