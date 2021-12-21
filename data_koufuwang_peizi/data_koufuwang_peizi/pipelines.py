import pymysql


class DataPipeline:
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="data_usable_database",
        autocommit=True
    )
    cursor = conn.cursor()
    def process_item(self, item, spider):
        if(spider.name == 'cofool_question_Spider'):
            sql = "INSERT INTO `data_usable_database`.`tb_cofool_question` (`tag`, `question`, `page_url`, `question_url`) VALUES (\'{}\', \'{}\', \'{}\', \'{}\');".format(
                item['tag'],
                item['question'],
                item['page_url'],
                item['question_url'],
            )
            res = self.cursor.execute(sql)
            print("数据库插入结果：", res, " sql: ",sql)
        elif(spider.name=='cofool_answer_Spider'):
            sql = "INSERT INTO `data_usable_database`.`tb_cofool_answer` (`question_id`, `answer`, `totle_answer`) VALUES (\'{}\', \'{}\', \'{}\');".format(
                item['question_id'],
                item['answer'],
                item['totle_answer']
            )
            res = self.cursor.execute(sql)
            if(res!=1):
                print("数据库插入结果：", res, " sql: ", sql)
        return item
