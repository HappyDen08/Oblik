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

    # Налаштування проксі для безкоштовного тарифу PythonAnywhere
    session = None
    if os.getenv("http_proxy"):
        from aiogram.client.session.aiohttp import AiohttpSession
        # trust_env=True дозволяє aiohttp автоматично використовувати системні проксі
        session = AiohttpSession()
        logging.info("Using system proxy via trust_env")

    bot = Bot(token=bot_token, session=session)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
