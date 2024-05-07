import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession


from config import (TELEGRAM_TOKEN)

from packeges.handlers import start_router, recive_file_router

session = AiohttpSession(
    api=TelegramAPIServer.from_base('http://localhost:8081'),
)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
    dp = Dispatcher()
    dp.include_routers(start_router.router,
                       recive_file_router.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())