from .items import ArticleInfoItem
from .items import CommentItem
import pymysql

class commentPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="commentdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if(isinstance(item, ArticleInfoItem)):
            url = item['url']
            publishTime = item['publishTime']
        elif(isinstance(item, CommentItem)):
            comment = item['comment']
            fromUrl = item['fromUrl']
            publishTime = item['publishTime']
            sql = "INSERT INTO `commentdatabase`.`tb_comment_xueqiu_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime
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
