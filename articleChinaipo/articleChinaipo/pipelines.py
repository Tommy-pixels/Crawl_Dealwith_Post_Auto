import pymysql
from auto_datahandler.basement__.ContralerTime import Contraler_Time

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
        if('\"' in content):
            content = content.replace("\"", "\'")
        _curDate = Contraler_Time.getCurDate(formatStr='%m-%d').split('-')
        if (_curDate[0] + '月' + _curDate[1] + '日' + '，资本邦了解到，' in content):
            content = content.replace(_curDate[0] + '月' + _curDate[1] + '日' + '，资本邦了解到，', '')
        if(len(content.replace('<p>','').replace('</p>',''))>515):
            sql = "INSERT INTO `articledatabase`.`tb_article_chinaipo_content` (`title`, `content`) VALUES (\"{}\", \"{}\");".format(
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
