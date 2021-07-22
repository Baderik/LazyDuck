import schedule
from time import sleep
from sys import path
from loguru import logger

path.append("../")

from storage.settings import LOGURU_PATH
from storage.services import update_storage

logger.add(LOGURU_PATH, rotation="1 day", compression="zip")

schedule.every().hour.at(":00").do(update_storage)

if __name__ == '__main__':
    update_storage()
    while True:
        schedule.run_pending()
        sleep(1)
