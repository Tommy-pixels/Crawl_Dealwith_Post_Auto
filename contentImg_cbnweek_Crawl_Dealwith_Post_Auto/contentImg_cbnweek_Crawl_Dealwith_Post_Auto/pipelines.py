import pymysql

class ContentimgPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="imgsdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        imgUrl = item['imgUrl']
        from_url = item['from_url']
        if(type(imgUrl) == str):
            sql = "INSERT INTO `imgsdatabase`.`tb_contentimg_cbnweek` (`origin_pic_path`,`from_url`) VALUES (\'{}\', \'{}\');".format(
                imgUrl,
                from_url
            )
            self.cursor.execute(sql)
        elif(type(imgUrl) == list):
            for url in imgUrl:
                sql = "INSERT INTO `imgsdatabase`.`tb_contentimg_cbnweek` (`origin_pic_path`,`from_url`) VALUES (\'{}\', \'{}\');".format(
                    url,
                    from_url
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