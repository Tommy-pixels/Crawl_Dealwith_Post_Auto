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
    paragraph_lis = []
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
        self.paragraph_lis.append(paragraph)
        return item

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
        print("- 站点：{} ; 爬取类型：{}; 关联段落总数：{};".format(spider.name, 'relative_paragraph', len(self.paragraph_lis)))