from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from asyncio import get_event_loop
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.webhook import get_new_configured_app

from bot.settings import API_TOKEN, WEBHOOK_PATH, WEBHOOK_URL


loop = get_event_loop()
print([API_TOKEN])
bot = Bot(API_TOKEN, loop=loop)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
app = get_new_configured_app(dispatcher=dispatcher, path=WEBHOOK_PATH)
