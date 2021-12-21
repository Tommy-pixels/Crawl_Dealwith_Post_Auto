import pymysql, time

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class ArticlePipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="articledatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        if (spider.name == 'huxiuSpider'):
            title = item['title']
            content = item['content']
            if('\'' in content):
                content = content.replace('\'', "\"")
            sql = "INSERT INTO `articledatabase`.`tb_article_huxiu_content` (`title`, `content`) VALUES (\'{}\',\'{}\');".format(
                title,
                content
            )
            # 执行Sql语句
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print("插入虎嗅网文章信息记录失败： ", sql)
        else:
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

