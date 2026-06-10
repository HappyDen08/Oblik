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
# бо WSGI-воркер синхронний. Луп створюємо ЛІНИВО, при першому запиті:
# uWSGI імпортує модуль у майстер-процесі й потім форкає воркера,
# а потоки форк не переживають — луп, запущений при імпорті, у воркері мертвий.
_loop = None
_loop_pid = None
_loop_lock = threading.Lock()


def get_loop():
    global _loop, _loop_pid
    with _loop_lock:
        if _loop is None or _loop_pid != os.getpid():
            _loop = asyncio.new_event_loop()
            _loop_pid = os.getpid()
            threading.Thread(target=_loop.run_forever, daemon=True).start()
            asyncio.run_coroutine_threadsafe(init_db(), _loop).result(timeout=30)
            logging.info(f"Event loop started in pid {_loop_pid}")
        return _loop


app = Flask(__name__)


@app.post("/webhook")
def telegram_webhook():
    if WEBHOOK_SECRET and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        abort(403)
    loop = get_loop()
    update = Update.model_validate(request.get_json(force=True), context={"bot": bot})
    # Відповідаємо Telegram одразу, обробка йде у фоні
    future = asyncio.run_coroutine_threadsafe(dp.feed_update(bot, update), loop)
    future.add_done_callback(_log_update_errors)
    return "ok"


def _log_update_errors(future):
    exc = future.exception()
    if exc:
        logging.exception("Update processing failed", exc_info=exc)


@app.get("/")
def health():
    return "Bot is running (webhook mode)"
