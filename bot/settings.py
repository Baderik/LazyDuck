from os import getenv
from os.path import join

API_TOKEN = getenv('TG_BOT_TOKEN')
if not API_TOKEN:
    # API_TOKEN = "1919016140:AAGXpdfQg_DIeIhLlwAk8qFX38Oe7ZAwHFA"
    exit(1)

# webhook settings
WEBHOOK_HOST = '7339436c0580.ngrok.io'
WEBHOOK_PATH = ''  # SECRET
WEBHOOK_URL = join(WEBHOOK_HOST, WEBHOOK_PATH)

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 5000

# handlers settings
ANSWERS = {
    "HELLO": "Привет я бот для отслеживания себя в списке ДВФУ",
    "INVALID_SNILS": "Снилс должен быть такого формата: 111-222-333 44",
    "RESET_STATE": "Мы вернулись в начало",
    "HELP": "Тут должно быть сообщение с помощью, но вы взрослый и справитесь сами\tУдачи)"
}
