import asyncio
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from bot import router
from conf import TELEGRAM_TOKEN
from utils import Logger

logger = Logger(name='main').logger


async def run():
    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router=router)
    await Dispatcher.start_polling(dp, bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Exited")
