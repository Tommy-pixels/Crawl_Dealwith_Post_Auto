import pymysql

class ArticlePipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if ('paragraph' in item.fields):
            # 文章内容的处理
            sql = "INSERT INTO " + item['dbName'] + ".`" + item[
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
            sql = "INSERT INTO " + item['dbName'] + ".`" + item[
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