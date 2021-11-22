import pymysql,time

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class commentsPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="commentdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        curTime = int(getSecondByDate(getCurDate() + " 00:00:00"))
        timeDelta = curTime - 172800000
        if(spider.name=='comment2Spider'):
            comment = item['comment']
            publishTime = item['publishTime']
            comment = comment.replace('[淘股吧]', '').replace('［图片］', '')
            sql = "INSERT INTO `commentdatabase`.`tb_comment_taoguba2_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime
            )
            if(publishTime>=timeDelta):
                self.cursor.execute(sql)
        elif(spider.name=='comment1Spider'):
            comment = item['comment']
            publishTime = item['publishTime']
            comment = comment.replace('[淘股吧]', '').replace('［图片］', '')
            sql = "INSERT INTO `commentdatabase`.`tb_comment_taoguba1_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime
            )
            if (publishTime >= timeDelta):
                self.cursor.execute(sql)
        return item

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
            print("关闭数据库连接成功")
        except Exception as e:
            print("关闭数据库连接失败")
