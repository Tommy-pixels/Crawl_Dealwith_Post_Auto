import pymysql

class ParagraphPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        autocommit=True
    )
    cursor = conn.cursor()
    paragraph_lis = []
    def process_item(self, item, spider):
        sql = "INSERT INTO `paragraphdatabase`.`tb_keyparagraph_selfsites_content` (`paragraph`, `tag_ori`) VALUES (\'{}\',\'{}\');".format(
            item['paragraph'],
            item['tag_ori'],
        )
        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(sql)
        self.paragraph_lis.append(item['paragraph'])
        return item


    def close_spider(self, spider):
        # 关闭数据库
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except Exception as e:
            print("关闭数据库连接失败")
            pass
        print("- 站点：{} ; 爬取类型：{}; 段落总数：{};".format(spider.name, 'keyparagraph', len(self.paragraph_lis)))