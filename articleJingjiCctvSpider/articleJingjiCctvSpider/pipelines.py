import pymysql, re

def del_brackets(s, sl,sr):
    r_rule = u"\\" + sl + u".*?" + sr
    return re.sub(r_rule, "", s)

class ArticlesPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="articledatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    title_lis = []
    def process_item(self, item, spider):
        title = item['title']
        content = item['content']
        if('\"' in content or '央视网消息' in content or '本报讯' in content):
            content = content.replace("\"", "\'").replace('央视网消息', '').replace('本报讯', '')
        content = del_brackets(content, sl='（记者', sr='）')
        if(content.startswith('：') or content.startswith(':')):
            content = content[1:]
        sql = "INSERT INTO `articledatabase`.`tb_article_cctvjingji_content` (`title`, `content`) VALUES (\"{}\", \"{}\");".format(
            title,
            content
        )
        self.title_lis.append(title)
        self.cursor.execute(sql)
        return item

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
        print("-站点：{} ; 爬取类型：{}; 文章总数：{};".format(spider.name, 'article', len(self.title_lis)))
        print("--文章title：")
        for title in self.title_lis:
            print('\t', title)
