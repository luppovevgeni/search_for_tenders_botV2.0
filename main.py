import asyncio
from aiogram import Bot, Dispatcher
from handlers import commands, reply_to_text, callback_data, pay
import config as config
import scheduler
import logging


logging.basicConfig(level=logging.DEBUG)


bot = Bot(token=config.TOKEN)
dp = Dispatcher()


async def main():
    scheduler.initialization()
    dp.include_router(commands.router)
    dp.include_router(callback_data.router)
    dp.include_router(reply_to_text.router)
    dp.include_router(pay.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())