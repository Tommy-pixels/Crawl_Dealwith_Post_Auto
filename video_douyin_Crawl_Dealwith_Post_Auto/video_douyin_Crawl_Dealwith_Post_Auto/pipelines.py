import pymysql

class VideoPipeline:
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
        print(item)
        # 在插入数据库前先判断数据库中是否存在对应视频数据
        sql_search = "SELECT * FROM `videodatabase`.`tb_douyin_videoinfo` WHERE `title`={}".format(
            item['title'])
        self.cursor.execute(sql_search)
        if (not self.cursor.fetchall()):
            sql = "INSERT INTO `videodatabase`.`tb_video_videoinfo` (`title`, `videoUrl`, `publishTime`, `duration`) VALUES (\'{}\',\'{}\',\'{}\', \'{}\');".format(
                item['title'],
                item['videoUrl'],
                item['publishTime'],
                item['duration']
            )
            self.cursor.execute(sql)
        else:
            print("数据库存在如下记录，插入记录失败")
            print(item)
            print("------------------------")
        return item

    def close_spider(self, spider):
        print('douyin爬虫关闭')


