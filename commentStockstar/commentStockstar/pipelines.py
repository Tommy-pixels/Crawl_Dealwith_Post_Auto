import pymysql
from auto_datahandler.customFunction__.Cleaner import base_cleaner

class FilterPipeline:
    def process_item(self, item, spider):
        filter_words = [
            'http', '：', ':', '解盘时间', '投资心得', '订阅地址', '早评：', '直播室', '订阅'
        ]
        for word in filter_words:
            if(word in item['comment']):
                item['comment'] = ''
        return item

class CleanPipeline:
    cleaner = base_cleaner.Base_Cleaner()
    def process_item(self, item, spider):
        if(item['comment']!=''):
            item['comment'] = self.cleaner.del_content_brackets(item['comment'], size='', o='', delAll=True)
        return item

class CommentPipeline:
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
        if(item['comment']!=''):
            comment = item['comment']
            publishTime = item['publishTime']
            # 评论的发布时间在两天内则录入数据库
            sql = "INSERT INTO `commentdatabase`.`tb_comment_stockstar_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                comment,
                publishTime,
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
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