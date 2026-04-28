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
    proxy_url = os.getenv("http_proxy")
    if proxy_url:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=proxy_url)
        logging.info(f"Using proxy: {proxy_url}")

    bot = Bot(token=bot_token, session=session)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logging.warning(f"Could not delete webhook (this is often normal on PythonAnywhere): {e}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
