import scrapy
import pymysql
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class ArticleContentPipeline:
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
        if('"' in content):
            content = content.replace('"', '\'')
        sql = "INSERT INTO `articledatabase`.`tb_article_cngold_content` (`title`, `content`) VALUES (\"{}\", \"{}\");".format(
            title,
            content
        )
        if (Base_Identifier.is_intterrogative(title)):
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
            self.title_lis.append(title)
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
            print('\t',title)
