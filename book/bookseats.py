import requests
import json
import time
from book.book_config import *
import logging
import datetime


class Book:
    def __init__(self, user_id, user_password, seat_number, time_start, book_time, room_name):
        """
        :param user_id: user id
            :type: string
            example: 201626702010
        :param user_password: user password
            :type: string
            example: 000000
        :param seat_number: book seat number
            :type: int
            example: 101
        :param time_start: book start time
            :type: string
            example: 8
        :param book_time: book time
            :type: string
            example: 12
        :param room_name: the room name
            :type: string
            example: 二楼南
        """
        self.user_Id = user_id
        self.user_password = user_password
        self.seat_Id = self.__get_seat_id(seat_number, room_name)
        self.time_start = self.__get_timestamp(time_start)
        self.book_time = str(int(book_time)*60*60)
        self.room_name = room_name

        # get the complete login data
        self.login_data = LOGIN_BASE_DATA
        self.login_data["login_name"] = self.user_Id
        self.login_data["password"] = self.user_password

        # create request session
        self.ss = requests.session()

        login_response = self.login()
        login_response = json.loads(login_response)
        if login_response and LOGIN_RESULT in login_response.keys():
            self.booker_id = login_response[LOGIN_RESULT]
            user_name = login_response["name"]
            self.login_result = "{}-{}  系统登陆成功...".format(user_name, user_id)
        else:
            self.login_result = "{} 登陆失败...".format(user_id)

    def __get_timestamp(self, time_start):
        """
        :param time_start: the book start time, should change it to a timestamp
            :type: string
            example: 8
        :return: return the a timestamp of time from param
            :type: string
            example: 1576713600
        """
        now = datetime.datetime.now()
        tomorrow_date = datetime.datetime.strftime(now + datetime.timedelta(days=1), "%Y-%m-%d")
        tomorrow_time = "{} {}:00:00".format(tomorrow_date, time_start)
        tomorrow_time_stamp = str(int(
            time.mktime(
                time.strptime(
                   tomorrow_time,
                   "%Y-%m-%d %H:%M:%S"
                )
            )
        ))
        return tomorrow_time_stamp

    def __get_seat_id(self, seat_number, room_name):
        """
        :param seat_number: the seat number
            :type: int
        :param room_name: the room name
            :type: string
            example: 二楼南
        :return: add 26198 to seat number and change it to str type
            :type: str
        """
        base_id = START_ID_OF_FLOOR_DICT[room_name]
        if type(base_id) == int:
            seat_number = seat_number + base_id
            seat_id = str(seat_number)
        else:
            seat_id = base_id[seat_number]
        return seat_id

    def login(self):
        """
        :return: the login result text of response
        """
        login_data = json.dumps(self.login_data)
        response = None
        try:
            response = self.ss.post(LOGIN_URL, data=login_data, headers=REQUEST_HEADER).text
        except Exception as e:
            logging.error(dict(
                message="The login is failed: {}".format(e),
                login_data=login_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            ))
        return response

    def book(self):
        """
        :return: the book result text of response
        """
        # the book data
        book_data = {
            'LAB_JSON': 1,
            'beginTime': self.time_start,
            'duration': self.book_time,
            'seats[0]': self.seat_Id,
            'seatBookers[0]': self.booker_id
        }
        response = None
        try:
            response = self.ss.post(url=BOOK_URL, data=book_data).text
        except Exception as e:
            logging.error(dict(
                message="The book is failed: {}".format(e),
                book_data=book_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            ))
        return response

    def get_seats_info(self):
        """
        :return: return the seats info by query conditions
        """
        seats_info = None
        # get seats info form data
        form_data = {
            "beginTime": self.time_start,
            "duration": self.book_time,
            "num": "1",
            "space_category[category_id]": "591",
            "space_category[content_id]": SEATS_INFO_ROOM_ID[self.room_name]
        }
        try:
            seats_info = requests.post(url=SEATS_INFO_URL, data=form_data).text
        except Exception as e:
            logging.error(dict(
                message="The search seats info is failed: {}".format(e),
                form_data=form_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            ))
        return seats_info
