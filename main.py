import time
import datetime
# 导入pymysql库
import pymysql


def gmt2utc(time):
    # 定义函数gmt2utc，用于将GMT时间转化为UTC时间
    gmt_time = datetime.datetime.strptime(time,
                                          '%Y-%m-%dT%H:%M:%S.%f+08:00')  # 使用datetime库函数strptime，把GMT时间转换为datetime类型
    utc_time = gmt_time - datetime.timedelta(hours=8)  # 计算UTC时间，减去8小时
    utc_time = utc_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 将utc_time转换为字符串，并且去除最后三位
    return utc_time  # 返回utc时间


# 建立mysql数据库连接
db = pymysql.connect(host="localhost", user="root", password="123", db="test")
cursor = db.cursor()  # 使用cursor()方法获取操作游标
sql = "insert into event (type,username,s_ip,s_port,d_ip,d_port,time) values (%s,%s,INET_ATON(%s),%s,INET_ATON(%s),%s,%s)"   #sql语句定义输入内容


item2: list = list()
item1: list = list()  #建立列表
print('run!!')
with open('/var/log/forensics.log', mode='r') as f:
    f.seek(0, 2)    #文件指针移到末尾
    while 1:

        line = f.readline()

        if len(line) == 0:
            time.sleep(1)
        else:

            if "Accepted" in line:  #ssh登录成功
                raw_date, raw_info = line.split(": ")   #分割文件
                date = raw_date.split()[0]
                infos = raw_info.split()
                user = infos[3]
                s_ip = infos[5]
                s_port = infos[7]
                d_ip = "自己定义下"
                d_port = "22"
                type = "auth.login.success"
                item1 = [type, user, s_ip, s_port, d_ip, d_port, gmt2utc(date)]
                cursor.execute(sql, item1)   #执行语句插入数据库
                db.commit()
                print('write!!')
                print(type, user, gmt2utc(date), s_ip, s_port, d_ip, d_port)
                f.seek(0, 2)

            if "Failed" in line:   #ssh登录失败
                raw_date, raw_info = line.split(": ")
                date = raw_date.split()[0]
                infos = raw_info.split()
                user = infos[3]
                s_ip = infos[5]
                s_port = infos[7]
                d_ip = "自己定义下"
                d_port = "22"
                type = "auth.login.failed"
                item2 = [type, user, s_ip, s_port, d_ip, d_port, gmt2utc(date)]
                cursor.execute(sql, item2)
                db.commit()
                print('write!!')
                print(type, user, gmt2utc(date), s_ip, s_port, d_ip, d_port)
                f.seek(0, 2)




from _socket import inet_ntoa

import pymysql  # 导入pymysql库

# 连接数据库
db = pymysql.connect(host="localhost", user="root", password="123", db="test")

# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

# 提示用户输入
num = int(input(
    '请输入数字：1.谁在昨晚9pm~10pm登录到本服务器？，2.从上次用户成功的登录root后，有多少失败的登录尝试？，3.root用户是最后登录的时间是什么？ '))

# 判断用户输入
if num == 1:
    # 执行 SQL 语句1
    cursor.execute("SELECT event_id,type,username,INET_NTOA(s_ip) as s_ip,s_port,INET_NTOA(d_ip) as d_ip,d_port,time FROM event WHERE time BETWEEN '2023-03-29 13:00:00' AND '2023-03-29 14:00:00'")

    # 获取所有记录列表
    results = cursor.fetchall()
    print('查询结果：', results)

elif num == 2:
    # 执行 SQL 语句
    sql = "SELECT MAX(event_id) - MIN(event_id) AS diff FROM (SELECT event_id FROM event WHERE type = 'auth.login.success' ORDER BY time DESC LIMIT 2) AS t;"
    cursor.execute(sql)
    result = cursor.fetchone()
    print("失败结果为：", result[0]-1)


elif num == 3:
    # 执行SQL插入语句
    sql = "SELECT * FROM event WHERE `username`='root' ORDER BY `time` DESC LIMIT 1"
    cursor.execute(sql)

    # 提交到数据库执行
    db.commit()
    results = cursor.fetchall()
    print('查询结果：', results)

# 关闭数据库连接
