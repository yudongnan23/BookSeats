import schedule
import time
from multiprocessing import Process, Pipe
from book.bookseats import Book
from doschedule.settings import *


def main():
    """ create multiprocess and Pipe, and starting book seats

    :return: return nothing
    """
    parent, child = Pipe()
    for i in range(5):
        # TODO: create multiprocess
        pass


def timer():
    """ create multiprocess and book seats every at every day 21:59:59

    :return: return nothing
    """
    schedule.every().day.at("21:59:59").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
