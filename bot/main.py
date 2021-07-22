from bot.core import dispatcher, bot
from bot.settings import WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL, WEBHOOK_PATH
from bot.handler import *
from aiogram.utils.executor import start_webhook
import logging


async def born(dp):
    dp.register_message_handler(h_start, commands=["start"])
    dp.register_message_handler(h_help, state="*", commands=["help"])
    dp.register_message_handler(h_cancel, state="*", commands=["cancel"])
    dp.register_message_handler(h_search, state="*", commands=["search"])
    dp.register_message_handler(h_info, state="*", commands=["info"])
    dp.register_message_handler(h_fsearch, state=searchState)

    # Setting webhook
    webhook = await bot.get_webhook_info()
    if webhook.url != WEBHOOK_URL:
        # If URL doesnt match current - remove webhook
        if not webhook.url:
            await bot.delete_webhook()

        # Set new URL for webhook
        await bot.set_webhook(WEBHOOK_URL)


async def die(dp):
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=born,
        on_shutdown=die,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
    )
