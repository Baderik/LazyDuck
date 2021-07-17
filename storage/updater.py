import schedule
from time import sleep
from sys import path

path.append("../")

from storage.services import update_storage

schedule.every().hour.at(":00").do(update_storage)

if __name__ == '__main__':
    update_storage()
    while True:
        schedule.run_pending()
        sleep(1)
