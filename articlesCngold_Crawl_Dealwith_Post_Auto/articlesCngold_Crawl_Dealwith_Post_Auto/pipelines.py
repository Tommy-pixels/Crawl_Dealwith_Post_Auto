import pymysql
from .items import ArticleContentItem, ArticleInfoItem

class ArticlesCngoldPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="paragraphdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        if(isinstance(item, ArticleInfoItem)):
            url = item['url']
            title = item['title']
            publishTime = item['publishTime']
            kind = item['kind']
            sql = "INSERT INTO `paragraphdatabase`.`tb_relativeParagraph_cngold_articleinfo`(`url`, `title`, `publishTime`, `kind`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\');".format(
                url,
                title,
                publishTime,
                kind
            )
            self.cursor.execute(sql)
        elif(isinstance(item, ArticleContentItem)):
            url = item['url']
            paragraph = item['paragraph']
            sql = "INSERT INTO `paragraphdatabase`.`tb_relativeParagraph_cngold_articlecontent` (`referArticleUrl`, `paragraph`) VALUES (\'{}\',\'{}\');".format(
                url,
                paragraph.strip()
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