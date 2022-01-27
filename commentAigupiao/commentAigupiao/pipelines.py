import pymysql, time
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

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
        sub_list = item['sub_list']
        comment = item['comment']
        publishTime = item['publishTime']
        yesterdaySeconds = int(getSecondByDate(str(getCurDate()) + ' 00:00:00')) - 172800 # 48h前的时间戳（秒）
        if("'" in comment):
            comment = comment.replace('\'','"')
        comment = Base_Cleaner.del_content_between(comment, '<', '>')
        comment = Base_Cleaner.del_content_between(comment, '[', ']')

        if(int(publishTime)>int(yesterdaySeconds)):
            # 评论的发布时间在两天内则录入数据库
            sql = "INSERT INTO `commentdatabase`.`tb_comment_aigupiao_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
            self.comment_lis.append(comment)

        if(sub_list):
            for sub_comment in sub_list:
                if (int(sub_comment[1]) > int(yesterdaySeconds)):
                    sub_comment_ = Base_Cleaner.del_content_between(sub_comment[0], '<', '>')
                    sub_comment_ = Base_Cleaner.del_content_between(sub_comment_, '[', ']')
                    # 评论的发布时间在两天内则录入数据库
                    sql = "INSERT INTO `commentdatabase`.`tb_comment_aigupiao_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                        sub_comment_,
                        sub_comment[1]
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
