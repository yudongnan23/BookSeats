import requests
import json
import time
from book.book_config import *
import logging
import datetime
import random

one_hour_timestamp = 1 * 60 * 60


class Book:
    def __init__(self, user_id: str, user_password: str,
                 seat_number: int, time_start: str, book_time: str, room_name: str):
        """  initialize the login and book's params, and login the system.

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
        # recode the book times
        self.book_times = 0
        # recode the get free seats info times
        self.get_free_seats_times = 0

        # take user_id, user password seat_id, book start time, book time and room name as instance variables
        self.user_Id = user_id
        self.user_password = user_password
        self.room_name = room_name
        self.seat_Id = self.__get_seat_id(seat_number)
        self.time_start = self.__get_timestamp(time_start)
        self.book_time = str(int(book_time) * one_hour_timestamp)

        # get the complete login data
        self.login_data = LOGIN_BASE_DATA
        self.login_data["login_name"] = self.user_Id
        self.login_data["password"] = self.user_password

        # create request session
        self.ss = requests.session()

        # get the login response
        login_response = self.login()
        login_response = json.loads(login_response)
        # judge the login is success or not
        if login_response and LOGIN_RESULT in login_response.keys():
            self.booker_id = login_response[LOGIN_RESULT]
            user_name = login_response["name"]
            self.login_result = "{}-{}  系统登陆成功...".format(user_name, user_id)
        else:
            self.login_result = "{} 登陆失败...".format(user_id)

    def __get_timestamp(self, time_start):
        """ get the time stamp, when now time's hour is greater than 17, will return tomorrow time stamp, if now time's
        is letter than 17, will return today time stamp.

        :param time_start: the book start time, should change it to a timestamp
            :type: string
            example: 8
        :return: return the a timestamp of time from param
            :type: string
            example: 1576713600
        """
        now = datetime.datetime.now()
        # get the now time's hour
        now_hour_time = int(datetime.datetime.strftime(now, "%H"))
        # if now time's hour is greater than 17, get tomorrow time stamp, if letter than 17, return today time stamp
        if now_hour_time > 17:
            tomorrow_date = datetime.datetime.strftime(now + datetime.timedelta(days=1), "%Y-%m-%d")
            tomorrow_time = "{} {}:00:00".format(tomorrow_date, time_start)
            time_stamp = str(int(
                time.mktime(
                    time.strptime(
                        tomorrow_time,
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            ))
        else:
            today_data = datetime.datetime.strftime(now, "%Y-%m-%d")
            today_time = "{} {}:00:00".format(today_data, time_start)
            time_stamp = str(int(
                time.mktime(
                    time.strptime(
                        today_time,
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            ))
        return time_stamp

    def __get_seat_id(self, seat_number):
        """ get the seats id from START_ID_OF_FLOOR_DICT in book_config.py.
        there is four rooms which can book.

        :param seat_number: the seat number
            :type: int
        :return: add 26198 to seat number and change it to str type
            :type: str
        """
        base_id = START_ID_OF_FLOOR_DICT[self.room_name]
        # get the seat id in four different rooms
        if type(base_id) == int:
            if self.room_name == "二楼南" and seat_number > 128:
                base_id = base_id + 1
            seat_number = seat_number + base_id
            seat_id = str(seat_number)
        else:
            seat_id = base_id[int(seat_number)]
        return seat_id

    def login(self):
        """ login the book system with login_data

        :return: the login result text of response
        """
        login_data = json.dumps(self.login_data)
        response = None
        try:
            response = self.ss.post(LOGIN_URL, data=login_data, headers=REQUEST_HEADER).text
        except Exception as e:
            logging.error(dict(
                message="The login is failed at line 138 in bookseats.py : {}".format(e),
                login_data=login_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            ))
        return response

    def book(self):
        """ book the seats in room after login successfully.

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

        try:
            self.book_times += 1
            response = self.ss.post(url=BOOK_URL, data=book_data, headers=BOOK_HEADER).text
        except Exception as e:
            logging.error(dict(
                message="The book is failed at line 164 in bookseats.py: {}".format(e),
                book_data=book_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

            ))
            return "服务器响应出错！\n系统提示：{}".format(e)

        # get the book result
        book_info, success = self.__get_book_result(response)

        # if book is not success and book times is letter than 6, get free seat id and book again
        if not success and self.book_times < 6:
            time.sleep(1)
            free_seats = self.__get_free_seats()
            # if not free seats, cancel book again, and return book info in below
            if not free_seats:
                book_info = "未知错误！服务器未返回正确数据！"
            else:
                free_seats_nums = len(free_seats)
                # get free seat id randomly in free seats list
                self.seat_Id = free_seats[random.randint(0, free_seats_nums - 1)]
                time.sleep(1)
                book_info = self.book()

        return book_info

    def __get_book_result(self, response):
        """ parse book result json text to get book result.

        :param response: the book result json text from book function
        :return: book result
        """
        result_dict = json.loads(response)
        book_info = None
        book_result = True
        try:
            user_name = result_dict["DATA"]["uname"]
        except Exception as e:
            book_result = False
            logging.error(dict(
                message="Get book result is failed at line 203 in bookseats.py: {}".format(e),
                book_response=result_dict,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            ))
            return book_info, book_result
        # if there is book result is "success", return book success info
        if "result" in result_dict["DATA"].keys() and result_dict["DATA"]["result"] == "success":
            book_info = "{}，恭喜您，座位预约成功！\n座位号：{}\n开始时间：{}\n预约时长：{}小时".format(
                user_name,
                self.__get_seat_number(),
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(self.time_start))),
                str(int(int(self.book_time) / one_hour_timestamp))
            )
        elif "result" in result_dict["DATA"].keys() and result_dict["DATA"]["result"] == "fail" and \
            result_dict["DATA"]["msg"] == "{}已有的预约，与当前预约时间有重叠".format(user_name) or \
                result_dict["DATA"]["msg"] == "{}已被加入黑名单，暂时无法预约".format(user_name):
            book_info = "{}, 非常抱歉，座位预约失败！\n系统提示：{}".format(
                user_name,
                result_dict["DATA"]["msg"]
            )
        elif "result" in result_dict["DATA"].keys() and result_dict["DATA"]["result"] == "fail":
            book_result = False
            book_info = "{}, 非常抱歉，座位预约失败！\n系统提示：{}".format(
                user_name,
                result_dict["DATA"]["msg"]
            )
        else:
            book_info = result_dict["CODE"]
        return book_info, book_result

    def __get_seat_number(self) -> str:
        """ get the seat number by seat id and room

        :return:
        """
        seat_number = 0
        seat_number_info = START_ID_OF_FLOOR_DICT[self.room_name]
        if type(seat_number_info) == dict:
            for key, value in seat_number_info.items():
                if value == self.seat_Id:
                    seat_number = key
        else:
            if self.room_name == "二楼南" and seat_number > 128:
                seat_number_info = seat_number_info + 1
            seat_number = str(int(self.seat_Id) - seat_number_info)
        return seat_number

    def __get_seats_info(self):
        """ get free seats info with book data.

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
            seats_info = self.ss.post(url=SEATS_INFO_URL, data=form_data, headers=BOOK_HEADER).text
        except Exception as e:
            logging.error(dict(
                message="The search seats info is failed at line 252 in bookseats.py: {}".format(e),
                form_data=form_data,
                error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            ))
        return seats_info

    def __get_free_seats(self):
        """ parse the json data from __get_seats_info function, if there is not free seats, takes book start time and
            book time minus one util getting the free seats.

        :return: return the free seats id and free time
        """
        self.get_free_seats_times += 1
        free_seats = []
        seats_info = json.loads(self.__get_seats_info())

        if seats_info:
            try:
                seats_info_list = seats_info["data"]["POIs"]
            except Exception as e:
                print(e)
                logging.error(dict(
                    message="Get free seats info is failed at line 273 in bookseats.py: {}".format(e),
                    seats_info=seats_info,
                    error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                ))
                return free_seats
        else:
            return free_seats

        # get the free seats id
        for single_seats_info in seats_info_list:
            if single_seats_info["state"] == 0 or single_seats_info["state"] == "0":
                free_seats.append(single_seats_info["id"])

        # if not free seats or get free seats times is greater than 3, take book start times minus one and get free
        # seats id again util getting free seats id
        if not free_seats or self.get_free_seats_times > 3:
            self.book_time = str(int(self.book_time) - one_hour_timestamp)
            self.time_start = str(int(self.time_start) + one_hour_timestamp)
            time.sleep(1)
            free_seats = self.__get_free_seats()

        return free_seats
