import schedule
import time
from multiprocessing import Process, Pipe
from book.bookseats import Book
from doschedule.settings import *


def book_seat(connection):
    """ create object of Book, and then book the seats

    :param 
    :return:
    """
    while True:
        try:
            user_info = connection.recv()
        except:
            return

        if user_info:

            booker = Book(user_id=user_info[0], user_password=user_info[1], seat_number=user_info[2],
                          time_start=user_info[3], book_time=user_info[4], room_name=user_info[5])
            print(booker.login_result)
            time.sleep(1)
            book_result = booker.book()
            print(book_result)


def main():
    """ create multiprocess and Pipe, and starting book seats

    :return: return nothing
    """
    parent_pipe, child_pipe = Pipe()

    process1 = Process(target=book_seat, args=(child_pipe,))
    process2 = Process(target=book_seat, args=(child_pipe,))
    process3 = Process(target=book_seat, args=(child_pipe,))

    for user_info in USER_INFO:
        parent_pipe.send(user_info)

    process1.start()
    process2.start()
    process3.start()

    parent_pipe.close()

    process1.join()
    process2.join()
    process3.join()


def timer():
    """ create multiprocess and book seats every at every day 21:59:59

    :return: return nothing
    """
    schedule.every().day.at("21:59:59").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
