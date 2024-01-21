import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, enums
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware
from aiohttp import web 
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers.commands import register_commands
from handlers.messages import register_messages
from handlers.callbacks import register_callbacks
from middlewares.db_check import DBCheck
from app.routes import check_crypto_payment, check_yookassa_payment
from tasks import register
import glv

glv.bot = Bot(glv.config['BOT_TOKEN'], parse_mode=enums.ParseMode.HTML)
glv.storage = MemoryStorage()
glv.dp = Dispatcher(storage=glv.storage)
app = web.Application()
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def on_startup(bot: Bot):
    asyncio.create_task(register())


def setup_routers():
    register_commands(glv.dp)
    register_messages(glv.dp)
    register_callbacks(glv.dp)


def setup_middlewares():
    i18n = I18n(path=Path(__file__).parent / 'locales', default_locale='ru', domain='bot')
    i18n_middleware = SimpleI18nMiddleware(i18n=i18n)
    i18n_middleware.setup(glv.dp)
    glv.dp.message.middleware(DBCheck())


async def main():
    setup_routers()
    setup_middlewares()
    glv.dp.startup.register(on_startup)

    setup_application(app, glv.dp, bot=glv.bot)
    await glv.dp.start_polling(glv.bot)


if __name__ == "__main__":
    asyncio.run(main())