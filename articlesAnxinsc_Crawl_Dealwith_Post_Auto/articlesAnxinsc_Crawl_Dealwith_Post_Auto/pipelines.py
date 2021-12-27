import pymysql


# 清洗掉空格和结尾的空格
def delSpace(paragraph):
    return paragraph.strip()

class ArticlePipeline:
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
        if ('paragraph' in item.fields):
            # 文章内容的处理
            sql = "INSERT INTO `paragraphdatabase`.`" + item[
                'tableName'] + "` (`url`, `paragraph`, `hasTag`) VALUES (\'{}\',\'{}\',\'{}\');".format(
                item['url'],
                delSpace(item['paragraph']),
                item['hasTag'],
            )
            try:
                self.cursor.execute(sql)
            except Exception as e:
                print(sql)
            self.paragraph_lis.append(item['paragraph'])
            return item
        elif ('title' in item.fields):
            # 文章列表的处理
            sql = "INSERT INTO `paragraphdatabase`.`" + item[
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

    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
        print("- 站点：{} ; 爬取类型：{}; 段落总数：{};".format(spider.name, 'keyparagraph', len(self.paragraph_lis)))