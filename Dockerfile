FROM ubuntu:18.04

COPY sources.list .
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
RUN mv sources.list /etc/apt/sources.list
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get upgrade && apt-get update

RUN apt-get install tzdata
# set timezone
ENV TZ=Asia/Shanghai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get install -y build-essential wget

RUN apt-get install -y python3.6 python3.6-dev python3-distutils

RUN wget https://bootstrap.pypa.io/get-pip.py && python3.6 get-pip.py -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .

RUN pip3.6 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR var/www/bookManager

COPY book book
COPY doschedule doschedule
COPY qq qq
COPY wechat wechat

ENTRYPOINT ["python3.6"]

CMD ["-m", "doschedule"]
