import pymysql,time, re

# 字符串正则处理类
class Handler_String_ByRe:
    def extract_StrByRe(self, s, patternStr=r'[[](.*?)[]]'):
        '''
        正则匹配字符串获取指定内容
        :param string: 待匹配的字符串
        :param patternStr: 正则表达式模式
        :return: 列表
        '''
        pattern = re.compile(patternStr, re.S)  # 最小匹配
        return re.findall(pattern, s)

class CommentsPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="commentdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    handler = Handler_String_ByRe()

    def process_item(self, item, spider):
        comment = item['comment']
        publishTime = item['publishTime']
        delLis = self.handler.extract_StrByRe(comment)
        for ite in delLis:
            comment = comment.replace('['+ite+']', '').strip()
        sql = "INSERT INTO `commentdatabase`.`tb_comment_guba_content` (`comment`, `publishTime`) VALUES (\'{}\', \'{}\');".format(
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
