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
    comment_lis = []
    def process_item(self, item, spider):
        if(item['comment']!=''):
            comments = item['comment']
            publishTime = item['publishTime']
            for comment in comments:
                if ('来源：' in comment or ':' in comment or '：' in comment or '报道' in comment):
                    continue
                if("'" in comment):
                    comment = comment.replace("'", '\"')
                comment = base_cleaner.Base_Cleaner.del_content_between(comment, '【','】')
                comment = base_cleaner.Base_Cleaner.del_content_between(comment, '（','）')
                comment = base_cleaner.Base_Cleaner.del_content_between(comment, '<','>')
                sql = "INSERT INTO `commentdatabase`.`tb_comment_futuniuniu_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
                    comment,
                    publishTime,
                )
                try:
                    self.cursor.execute(sql)
                except Exception as e:
                    print(sql)
                self.comment_lis.append(comment)
        return item

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
        print("- 站点：{} ; 爬取类型：{}; 评论总数：{};".format(spider.name, 'comment', len(self.comment_lis)))
