import scrapy
import pymysql
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class ArticlePipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="dbfreeh",
        autocommit=True
    )
    cursor = conn.cursor()
    title_lis = []
    def process_item(self, item, spider):
        print(spider.name)
        if(spider.name != 'csdnarticleSpider'):
            print('not csdnarticleSpider')
            title = item['title']
            # article_id = item['article_id']
            create_time = item['create_time']
            url = item['url']
            crawl_time = item['crawl_time']
            sql = "INSERT INTO `dbfreeh`.`tb_article` (`ori_url`, `title`, `content`, `publish_time`, `crawl_time`, `site`, `classification`) VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\");".format(
                url, title, '', create_time, crawl_time, 'CSDN', '新数据池系统'
            )
            _url = url.split('?')[0]
            try:
                self.cursor.execute('SELECT * FROM `dbfreeh`.`tb_article` WHERE `ori_url` like \'{}%\';'.format(_url))
                res = self.cursor.fetchall()
                if (not res):
                    self.cursor.execute(sql)
                else:
                    print('存在 {}, {}'.format(title,res))
            except Exception as e:
                print(sql)
            self.title_lis.append(title)
            return item
        else:
            print('is csdnarticleSpider')
            content = item['content']
            if ('"' in content):
                content = content.replace('"', '\'')
            id_a = item['id_a']
            sql = "UPDATE `dbfreeh`.`tb_article` SET `content`= \"{}\" WHERE (`id`=\"{}\");".format(
                content, id_a
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print('更新content: ', sql)
            self.title_lis.append(id_a)
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
