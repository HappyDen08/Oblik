"""Одноразовий скрипт: реєструє вебхук у Telegram.

Запуск (з консолі PythonAnywhere або локально):
    WEBHOOK_URL=https://<username>.pythonanywhere.com/webhook python -m app.bot.set_webhook
"""
import asyncio
import os

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()


async def main():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("WEBHOOK_URL is not set, e.g. https://<username>.pythonanywhere.com/webhook")

    session = None
    proxy_url = os.getenv("http_proxy")
    if proxy_url:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=proxy_url)

    bot = Bot(token=os.getenv("BOT_TOKEN"), session=session)
    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=os.getenv("WEBHOOK_SECRET") or None,
            drop_pending_updates=True,
        )
        info = await bot.get_webhook_info()
        print(f"Webhook set: {info.url}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
