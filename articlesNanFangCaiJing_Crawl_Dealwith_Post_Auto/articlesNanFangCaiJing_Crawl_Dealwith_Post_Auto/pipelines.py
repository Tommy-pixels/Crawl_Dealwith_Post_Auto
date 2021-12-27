"""
    这里爬取的是文章信息的列表
"""
import pymysql
from .items import articleContentItem, articleInfoItem

class articleInfoPipeline:
    # 设置数据库
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
        # 当需要处理多个item时用isinstance， 注意使用前引入对应item
        if(isinstance(item, articleInfoItem)):
            url = item["url"]
            title = item["title"]
            publishTime = item["publishTime"]
            kind = item['kind']
            sql = "INSERT INTO `paragraphdatabase`.`tb_relativeparagraph_nanfangcaifu_articleinfo` (`url`, `title`, `publishTime`, `kind`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\');".format(
                url,
                title,
                publishTime,
                kind
            )
            self.cursor.execute(sql)
        elif(isinstance(item, articleContentItem)):
            url = item['url']
            paragraph = item['paragraph']
            sql = "INSERT INTO `paragraphdatabase`.`tb_relativeparagraph_nanfangcaifu_articlecontent` (`referArticleUrl`, `paragraph`) VALUES (\'{}\',\'{}\');".format(
                url,
                paragraph.strip()
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
