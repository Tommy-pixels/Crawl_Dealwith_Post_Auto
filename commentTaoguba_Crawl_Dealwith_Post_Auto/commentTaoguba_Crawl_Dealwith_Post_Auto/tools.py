import pymysql
import time, random

def randomSleep(num):
    sleepTime = random.randint(0,num)
    time.sleep(sleepTime)
    pass

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d')
    return int(time.mktime(b))

def getSecondByFormat(date, formatStr='%Y-%m-%d %H:%M:%S'):
    b = time.strptime(date, formatStr)
    return int(time.mktime(b))

def getSecond():
    return int(round(time.time()))

class DBConnector:
    def __init__(self):
        self.user = 'root'
        self.passwd = 'root'
        self.databaseName = 'commentdatabase'
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        return pymysql.connect(
            host='localhost',
            user=self.user,
            password=self.passwd,
            db=self.databaseName,
            autocommit=True
        )

    def getOneSQL(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def updateSQL(self, sql):
        self.cursor.execute(sql)

    def closeDB(self):
        self.cursor.close()
        self.conn.close()