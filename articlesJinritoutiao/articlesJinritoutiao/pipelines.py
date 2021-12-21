import pymysql
from .tools import basic

class ArticlePipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="imgsdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        if(spider.name == 'toutiaoSpider'):
            sql = "INSERT INTO `data_usable_database`.`tb_toutiao_content` (`title`, `paragraph`) VALUES (\'{}\', \'{}\');".format(
                item["articleTitle"],
                item["paragraph"]
            )
            # 执行Sql语句
            try:
                result = self.cursor.execute(sql)
            except Exception as e:
                print("插入头条文章记录失败： ", sql)
        elif(spider.name == 'toutiaoImgsSpider'):
            pass
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

