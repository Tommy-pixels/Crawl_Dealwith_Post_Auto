import pymysql
from .tools import basic

class ToutiaoArticleInfoPipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="imgsdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        if(spider.name == 'toutiaoArticleInfoSpider'):
            title = item['title']
            article_url = item['article_url']
            share_url = item['share_url']
            behot_time = item['behot_time']
            group_id = item['group_id']
            has_image = item['has_image']
            user_name = item['user_name']
            user_id = item['user_id']
            user_avatarUrl = item['user_avatarUrl']
            sql = "INSERT INTO `tb_articlestoutiaocaijing` (`title`, `article_url`, `share_url`,`behot_time`, `group_id`, `has_image`, `user_name`, `user_id`, `user_avatarUrl`) VALUES (\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\',\'{}\');".format(
                title,
                article_url,
                share_url,
                behot_time,
                group_id,
                has_image,
                user_name,
                user_id,
                user_avatarUrl
            )
            # 执行Sql语句
            try:
                result = self.cursor.execute(sql)
                if (result == 1):
                    print("插入头条文章信息记录成功： ", item)
                    pass
            except Exception as e:
                print("插入头条文章信息记录失败： ", sql)
        elif(spider.name == 'toutiaoImgsSpider'):
            pass

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

