import pymysql, time

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class CommentgelonghuiPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="commentdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        comment = item['comment']
        publishTime = item['publishTime']
        yesterdaySeconds = int(getSecondByDate(str(getCurDate()) + ' 00:00:00')) - 172800 # 48h前的时间戳（秒）
        if(int(publishTime)>int(yesterdaySeconds)):
            # 评论的发布时间在两天内则录入数据库
            sql = "INSERT INTO `commentdatabase`.`tb_comment_gelonghui_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime
            )
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
