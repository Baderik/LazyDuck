from os import getenv, path

import loguru
from loguru import logger

API_TOKEN = getenv('TG_BOT_TOKEN')
if not API_TOKEN:
    logger.exception("TG_BO_TOKEN did not find")
    exit(1)

# webhook settings
WEBHOOK_HOST = getenv("WEBHOOK_HOST")
logger.info("WEBHOOK HOST variable: " + WEBHOOK_HOST)
WEBHOOK_PATH = getenv("WEBHOOK_PATH")  # SECRET
logger.info("WEBHOOK PATH variable: " + WEBHOOK_PATH)
WEBHOOK_URL = path.join(WEBHOOK_HOST, WEBHOOK_PATH)

# webserver settings
WEBAPP_PORT = getenv("PORT")

# handlers settings
ANSWERS = {
    "HELLO": "Привет я бот для отслеживания себя в списке ДВФУ",
    "INVALID_SNILS": "Снилс должен быть такого формата: 111-222-333 44",
    "RESET_STATE": "Мы вернулись в начало",
    "HELP": "Тут должно быть сообщение с помощью, но вы взрослый и справитесь сами\tУдачи)"
}
