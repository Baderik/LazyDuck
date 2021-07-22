from aiohttp import web

from bot.core import app, dispatcher, bot
from bot.settings import WEBAPP_PORT, WEBHOOK_URL
from bot.handler import h_start, h_cancel, h_help, h_search, h_fsearch, searchState


async def born(app):
    dispatcher.register_message_handler(h_start, commands=["start"])
    dispatcher.register_message_handler(h_help, state="*", commands=["help"])
    dispatcher.register_message_handler(h_cancel, state="*", commands=["cancel"])
    dispatcher.register_message_handler(h_search, state="*", commands=["search"])
    dispatcher.register_message_handler(h_fsearch, state=searchState)

    # Setting webhook
    webhook = await bot.get_webhook_info()
    if webhook.url != WEBHOOK_URL:
        # If URL doesnt match current - remove webhook
        if not webhook.url:
            await bot.delete_webhook()

        # Set new URL for webhook
        await bot.set_webhook(WEBHOOK_URL)


async def die(app):
    await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

app.on_startup.append(born)
app.on_shutdown.append(die)

web.run_app(app, port=WEBAPP_PORT)
