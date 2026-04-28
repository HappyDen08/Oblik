import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from app.bot.handlers import router
from app.database import init_db
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "your_bot_token_here":
        logging.error("BOT_TOKEN is not set!")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
