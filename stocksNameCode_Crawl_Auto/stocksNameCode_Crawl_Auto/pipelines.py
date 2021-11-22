import pymysql

class StocksnamecodePipeline:
    # 设置数据库
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="huxiudatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def process_item(self, item, spider):
        sql = "INSERT INTO `stocksnamecode`.`tb_namecode` (`name`, `code`, `belong`) VALUES (\'{}\',\'{}\',\'{}\');".format(
            item['name'],
            item['code'],
            item['belong']
        )
        self.cursor.execute(sql)
        return item
