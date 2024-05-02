import asyncio
from aiogram import Bot, Dispatcher

from config import (TELEGRAM_TOKEN)

from packeges.handlers import start_router, recive_file_router

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_routers(start_router.router,
                       recive_file_router.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())