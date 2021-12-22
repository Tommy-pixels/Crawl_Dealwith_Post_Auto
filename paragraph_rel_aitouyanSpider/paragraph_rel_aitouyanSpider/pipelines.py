import pymysql

class ParagraphPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="paragraphdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        paragraph = item['paragraph']
        if('\'' in paragraph):
            paragraph = paragraph.replace('\'','"')
        referArticleUrl = item['referArticleUrl']
        sql = "INSERT INTO `paragraphdatabase`.`tb_relativeparagraph_aitouyan_articlecontent` (`paragraph`, `referArticleUrl`) VALUES (\'{}\', \'{}\');".format(
            paragraph,
            referArticleUrl
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
