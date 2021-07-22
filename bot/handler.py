from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State

from bot.settings import ANSWERS
from bot.services import find_snils
from storage.services import find_applicant

__all__ = ["searchState",
           "h_start", "h_info", "h_help",
           "h_cancel", "h_search", "h_fsearch"]

searchState = State()


async def h_start(message: types.Message):
    return await message.reply(text=ANSWERS["HELLO"], reply=not message.chat.type == "private")


async def h_cancel(message: types.Message, state: FSMContext):
    await state.reset_state()
    return await message.reply(text=ANSWERS["RESET_STATE"], reply=not message.chat.type == "private")


async def h_help(message: types.Message, state: FSMContext):
    await state.reset_state()
    return await message.reply(text=ANSWERS["HELP"], reply=not message.chat.type == "private")


async def h_search(message: types.Message):
    arguments = message.get_args()
    if not (snils := find_snils(arguments)):
        await searchState.set()
        return await message.reply(text=ANSWERS["INVALID_SNILS"], reply=not message.chat.type == "private")

    if not (answer := find_applicant(snils)):
        answer = "Вас нет в списках ДВФУ"

    return await message.reply(text=f"СНИЛС: {snils}\n" + answer, reply=not message.chat.type == "private",
                               parse_mode='Markdown')


async def h_fsearch(message: types.Message, state: FSMContext):
    if not (snils := find_snils(message.text)):
        return await message.reply(text=ANSWERS["INVALID_SNILS"], reply=not message.chat.type == "private")

    await state.reset_state()
    if not (answer := find_applicant(snils)):
        answer = "Вас нет в списках ДВФУ"
    return await message.reply(text=answer, reply=not message.chat.type == "private",
                               parse_mode='Markdown')


async def h_info(message: types.Message, state: FSMContext):
    await state.reset_state()
    return await message.reply(text=ANSWERS["INFO"], reply=not message.chat.type == "private")
