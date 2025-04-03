from aiogram import Bot, Dispatcher
from app.handlers import router
from cfg import TOKEN
import asyncio
import logging


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
