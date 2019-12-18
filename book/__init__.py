import logging
import datetime
import time

logging.error(dict(
    message="123",
    data="1234",
    error_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
))