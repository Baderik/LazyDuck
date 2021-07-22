from os import getenv
from loguru import logger
from pathlib import Path

# DIRS
BASE_DIR = Path(__file__).resolve().parent.parent
LOGURU_DIR = BASE_DIR / "bot" / "logs"
LOGURU_PATH = LOGURU_DIR / "bot.log"

logger.add(LOGURU_PATH, rotation="1 day", compression="zip")

API_TOKEN = getenv('TG_BOT_TOKEN')
if not API_TOKEN:
    logger.exception("TG_BO_TOKEN did not find")
    exit(1)

# webhook settings
WEBHOOK_HOST = getenv("WEBHOOK_HOST")
logger.info("WEBHOOK HOST variable: " + WEBHOOK_HOST)
WEBHOOK_PATH = getenv("WEBHOOK_PATH")  # SECRET
logger.info("WEBHOOK PATH variable: " + WEBHOOK_PATH)
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH
logger.info("WEBHOOK URL variable: " + WEBHOOK_URL)


# webserver settings
WEBAPP_HOST = getenv("WEBAPP_HOST")
WEBAPP_PORT = int(getenv("PORT"))
logger.info("WEBAPP HOST variable: " + WEBAPP_HOST)
logger.info(f"WEBAPP PORT variable: {WEBAPP_PORT}")
# handlers settings
ANSWERS = {
    "HELLO": "Привет, я бот для отслеживания абитуриентов в списках ДВФУ.\nВведи /help, чтобы узнать больше.",
    "INVALID_SNILS": "Введите СНИЛС абитуриента",
    "RESET_STATE": "Мы вернулись в начало",
    "HELP": "Вы достаточно взрослый, чтобы справляться самостоятельно...",
    "INFO": "Туть будет информация...\nКогда-нибудь....\nЯ надеюсь..."
}
