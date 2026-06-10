"""Webhook-режим бота для PythonAnywhere (WSGI/Flask).

PythonAnywhere free не підтримує always-on процеси, тому поллінг
постійно вбивається. Натомість веб-додаток працює завжди — Telegram
надсилає оновлення POST-запитом на /webhook, а ми передаємо їх
у aiogram Dispatcher через фоновий event loop.
"""
import asyncio
import logging
import os
import threading

from flask import Flask, abort, request

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv

from app.bot.handlers import router
from app.database import init_db

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot_token = os.getenv("BOT_TOKEN")
if not bot_token or bot_token == "your_bot_token_here":
    raise RuntimeError("BOT_TOKEN is not set!")

# Секрет, яким Telegram підписує кожен запит (захист від чужих POST-ів)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

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

# Весь asyncio-код (aiogram, aiosqlite) живе на одному фоновому лупі,
# бо WSGI-воркер синхронний.
loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()
asyncio.run_coroutine_threadsafe(init_db(), loop).result(timeout=30)

app = Flask(__name__)


@app.post("/webhook")
def telegram_webhook():
    if WEBHOOK_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        abort(403)
    update = Update.model_validate(request.get_json(force=True), context={"bot": bot})
    # Відповідаємо Telegram одразу, обробка йде у фоні
    asyncio.run_coroutine_threadsafe(dp.feed_update(bot, update), loop)
    return "ok"


@app.get("/")
def health():
    return "Bot is running (webhook mode)"
