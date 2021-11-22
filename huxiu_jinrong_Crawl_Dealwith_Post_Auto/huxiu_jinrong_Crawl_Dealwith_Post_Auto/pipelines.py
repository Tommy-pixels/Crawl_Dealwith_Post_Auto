# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql, time

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class huxiuArticlePipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="huxiudatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        if (spider.name == 'huxiuSpider'):

            # if ('天前' not in item['formatDate'] and '小时前' not in item['formatDate'] and '分钟前' not in item['formatDate']):
            #     # 当满足某一条件则认定爬取完成，关闭爬虫
            #     if(getSecondByDate("".join(item['formatDate'].split('-')) + " 00:00:00") < getSecondByDate("20210917 00:00:00")):
            #         self.close_spider()


            # 将发布日期转换为时间戳，根据时间戳进行判断
            if('天前' not in item['formatDate'] and '小时前' not in item['formatDate'] and '分钟前' not in item['formatDate'] ):
                check = getSecondByDate("".join(item['formatDate'].split('-')) + " 00:00:00") > getSecondByDate(getCurDate() + " 00:00:00")
            else:
                check = False
            # if('天前' in item['formatDate'] or int(item['formatDate'].split('-')[1].lstrip('0')) >=8):
            if ('天前' in item['formatDate'] or '小时前' in item['formatDate'] or '分钟前' in item['formatDate'] or check):
                dateline = item['dateline']
                formatDate = item['formatDate']
                origin_pic_path = item['origin_pic_path']
                pic_path = item['pic_path']
                title = item['title']
                user_name = item['user_name']
                user_uid = item['user_uid']
                user_avatar = item['user_avatar']
                databaseTbName = item['databaseTbName']
                sql = "INSERT INTO `huxiudatabase`.`" + databaseTbName +"` (`dateline`, `formatDate`, `origin_pic_path`, `pic_path`, `title`, `user_name`, `user_uid`, `user_avatar`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\');".format(
                    dateline,
                    formatDate,
                    origin_pic_path,
                    pic_path,
                    title,
                    user_name,
                    user_uid,
                    user_avatar
                )

                # 执行Sql语句
                try:
                    result = self.cursor.execute(sql)
                    if (result == 1):
                        print("插入虎嗅网文章信息记录成功： ", item)
                        pass
                except Exception as e:
                    print("----------------------------------------")
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

