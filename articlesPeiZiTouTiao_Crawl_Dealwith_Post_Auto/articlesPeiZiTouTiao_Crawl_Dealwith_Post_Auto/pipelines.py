import pymysql


class ArticlesInfoPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="peizitoutiaodatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if(spider.name=='ArticlesInfoSpider'):
            sql = "INSERT INTO `peizitoutiaodatabase`.`" + item['tableName'] + "` (`title`, `publishTime`, `author`, `url`,`tag_origin`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\',\'{}\');".format(
                item['title'],
                item['publishTime'],
                item['author'],
                item['url'],
                item['tag']
            )
            self.cursor.execute(sql)
        return item
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

class ArticlesContentPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="peizitoutiaodatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if (spider.name == 'ArticlesContentSpider'):
            sql = "INSERT INTO `peizitoutiaodatabase`.`tb_" + item['tableName'] + "_articlecontent` (`paragraph`, `infoId`, `hasTag`) VALUES (\'{}\',\'{}\',\'{}\');".format(
                item['paragraph'],
                item['infoId'],
                item['hasTag'],
            )
            self.cursor.execute(sql)
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


class ArticlePipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="peizitoutiaodatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if ('paragraph' in item.fields):
            # 文章内容的处理
            sql = "INSERT INTO `peizitoutiaodatabase`.`" + item[
                'tableName'] + "` (`url`, `paragraph`, `hasTag`) VALUES (\'{}\',\'{}\',\'{}\');".format(
                item['url'],
                item['paragraph'],
                item['hasTag'],
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
            return item
        elif ('title' in item.fields):
            # 文章列表的处理
            sql = "INSERT INTO `peizitoutiaodatabase`.`" + item[
                'tableName'] + "` (`title`, `url`, `publishTime`, `tag_origin`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\');".format(
                item['title'],
                item['url'],
                item['publishTime'],
                item['tag']
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
            return item
