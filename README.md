# BookSeats
## 项目简介
* 在很多大学图书馆都会有提供给学生自习的自习室，但是自习室的座位却往往很难抢到，相信大部分的考研狗深有体会。接下来我以我学校的自习室预约座位系统为例，一步步实现座位预约，希望能给读者带来帮助，这就是该项目的意义及目的。

## 前期工作
### 开发工具
* pycharm专业版
* FireFox浏览器
### 需要安装的库
* python的第三方库requests（conda install requests或者pip install requests）

## 抓包过程
### 在抓包的过程中需要弄清楚的几个问题
* 抓取登陆请求的Url
* 抓取登陆请求的数据类型及结构


![logindata](https://github.com/yudongnan23/BookSeats/blob/master/logindata.jpg)


* 抓取预约座位时请求的Url
* 抓取预约座位时向客户端请求的数据及结构


![book](https://github.com/yudongnan23/BookSeats/blob/master/book.jpg)


# 代码实现
* 参考库中的bookseats.py文件
## 具体思路
* 首先定义各类数据，需要访问的Url

```python


        self.user_Id = user_Id                      # 学号
        self.user_password = user_password          # 登录密码
        self.seat_Id = seat_Id                      # 预定座位号
        self.time_from = time_from                  # 预定开始时间
        self.book_time = book_time                  # 预定时间

        # 登录访问url
        self.login_url = 'https://jxnu.huitu.zhishulib.com/api/1/login'
        # seatBookers数据提取url
        self.data_get_url = 'https://jxnu.huitu.zhishulib.com/Seat/Index/searchSeats?LAB_JSON=1'
        # 座位预定url
        self.book_url = 'https://jxnu.huitu.zhishulib.com/Seat/Index/bookSeats?LAB_JSON=1'


        # 定义网页请求头
        self.request_headers = {
            'Host': 'jxnu.huitu.zhishulib.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://jxnu.huitu.zhishulib.com/',
            'content-type': 'text/plain',
            'Content-Length': '262',
            'Connection': 'keep-alive',
            'Cookie': 'web_language=zh-CN'
        }


        # 定义登录提交的表单数据
        self.login_data = {
            "login_name": self.user_Id,
            "password": self.user_password,
            "org_id": "142",
            "_ApplicationId": "lab4",
            "_JavaScriptKey": "lab4",
            "_ClientVersion": "js_xxx",
            '_InstallationId': '48ebf6af-881b-d19f-5ff3-3eab4844610c',
            '_JavaScriptKey': 'lab4',
            'code': '0dcab0ba032be24743dc5e68510171e2',
            'str': '8jmGS9R365DtmauJ'
        }
```

* 创建session会话，创建该会话，系统将会自动保存cookie信息，在登陆之后可以继续发送预约座位的信息，无需重新登陆

```python

        #定义会话session
        self.ss = requests.session()
```

* 执行登陆函数（登陆函数具体代码如下：）
```python


    # 定义登录函数
    def login(self):
        data = json.dumps(self.login_data)
        rsp = self.ss.post(self.login_url,data = data, headers = self.request_headers).text
```
* 执行预约座位的函数(预约座位函数代码如下：)
```python



    # 定义预定提交函数
    def book(self):
        # 将预定开始时间转化为时间戳
        time_from = time_change(self.time_from)
        # 将预定时间转换为格式化类型
        book_time = str(int(self.book_time)*60*60)
        # 获取seatBookers的参数
        booker = self.getseatBooker()
        # 获取预定位置码
        seat_Id = search(self.seat_Id)
        # 定义预定座位提交的表单数据
        book_data = {
            'LAB_JSON': 1,
            'beginTime': time_from,
            'duration': book_time,
            'seats[0]': seat_Id,
            'seatBookers[0]':booker
        }
        rsp = self.ss.post(url = self.book_url,data = book_data)
        return rsp.text
```

#### 希望以上内容能对读者有所帮助！
