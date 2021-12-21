import scrapy
import pymysql


class ArticleContentPipeline:
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
        title = item['title']
        content = item['content']
        sql = "INSERT INTO `articledatabase`.`tb_article_aigupiao_content` (`title`, `content`) VALUES (\"{}\", \"{}\");".format(
            title,
            content
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
