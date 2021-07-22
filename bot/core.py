from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from asyncio import get_event_loop
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger

from bot.settings import API_TOKEN


loop = get_event_loop()

logger.info(f"Started bot with API token: {API_TOKEN}")

bot = Bot(API_TOKEN, loop=loop)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
