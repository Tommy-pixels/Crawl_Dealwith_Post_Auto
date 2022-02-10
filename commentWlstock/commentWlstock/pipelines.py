import pymysql, time

# 获取当前日期
def getCurDate(format="%Y%m%d"):
    return time.strftime(format, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class CommentPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="commentdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    comment_lis = []
    def process_item(self, item, spider):
        comment = item['comment']
        publishTime = int(getSecondByDate(getCurDate('%Y') + item['publishTime'] + ' 00:00:00'))
        yesterdaySeconds = int(getSecondByDate(str(getCurDate('%Y%m%d')) + ' 00:00:00')) - 172800 # 48h前的时间戳（秒）
        if("'" in comment):
            comment = comment.replace('\'','"')
        if(int(publishTime)>int(yesterdaySeconds)):
            if(not self.cursor.execute("SELECT * FROM `commentdatabase`.`tb_comment_wlstock_content` WHERE `comment`=\'{}\'".format(comment))):
                # 评论的发布时间在两天内则录入数据库
                sql = "INSERT INTO `commentdatabase`.`tb_comment_wlstock_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                    comment,
                    publishTime
                )
                try:
                    self.cursor.execute(sql)
                except Exception as e:
                    print(sql)
                self.comment_lis.append(comment)
        return item

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
        print("- 站点：{} ; 爬取类型：{}; 评论总数：{};".format(spider.name, 'comment', len(self.comment_lis)))
