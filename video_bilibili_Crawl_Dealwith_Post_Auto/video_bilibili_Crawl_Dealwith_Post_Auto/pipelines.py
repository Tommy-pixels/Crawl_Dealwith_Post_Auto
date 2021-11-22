import pymysql


class videoPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="videodatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        print("pipeline")
        # 在插入数据库前先判断数据库中是否存在对应视频数据
        sql_search = "SELECT * FROM `videodatabase`.`tb_bilibili_videoinfo` WHERE `avValue` = {}".format(item['avValue'])
        self.cursor.execute(sql_search)
        if(not self.cursor.fetchall()):
            sql = "INSERT INTO `videodatabase`.`tb_bilibili_videoinfo` (`title`, `bilibiliUrl`, `avValue`, `cid`, `videoUrl`, `pubdate`, `duration`) VALUES (\'{}\',\'{}\',\'{}\', \'{}\', \'{}\', \'{}\', \'{}\');".format(
                item['title'],
                item['bilibiliUrl'],
                item['avValue'],
                item['cid'],
                item['videoUrl'],
                item['pubdate'],
                item['duration']
            )
            self.cursor.execute(sql)
        else:
            print("数据库存在如下记录，插入记录失败")
            print(item)
            print("------------------------")
        return item

    def close_spider(self, spider):
        # 关闭chromedriver
        spider.browser.quit()
        print('bilibili爬虫关闭')

