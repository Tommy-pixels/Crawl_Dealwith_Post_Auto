import pymysql
import requests
import hashlib, time
from requests_toolbelt import MultipartEncoder

# 从数据库获取对应数据并清洗输出可上传的数据
class GetPostableData():
    def __init__(self,topicName):
        self.topicName = topicName
        self.filterWord = []
        for i in range(1, 10):
            self.filterWord.append(str(i) + '.')
            self.filterWord.append(str(i) + '，')
            self.filterWord.append(str(i) + '、')
        self.filterWord = tuple(self.filterWord)
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(
            host='localhost',
            user="root",
            passwd="root",
            db="peizitoutiaodatabase",
            autocommit=True
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()
        pass

    def getData(self):
        sql = "SELECT * FROM peizitoutiaodatabase.tb_"+ self.topicName +"_articlecontent;"
        self.cursor.execute(sql)
        tempResult = self.cursor.fetchall()
        result = []
        for item in tempResult:
            result.append(
                [
                    item[0],
                    item[1],
                    item[2],
                    item[3]
                ]
            )
        return result

    def getTagFromDatabase(self, infoId):
        sql = "SELECT `tag_origin` FROM peizitoutiaodatabase.tb_" + self.topicName + "_articleinfo WHERE `id`=" + str(infoId) + ";"
        self.cursor.execute(sql)
        return self.cursor.fetchone()[0]

    def filter_Between120to250(self, paragraph):
        if(len(paragraph) > 125 and len(paragraph) < 250):
            return True
        else:
            return False

    def filter_delSpace(self, paragraph):
        return paragraph.replace("\r\n\t","").replace("\xa0","")

    # 删除开头的序号
    def filter_delHeaderNum(self, paragraph):
        for filterword in self.filterWord:
            paragraph = paragraph.lstrip(filterword)
        return paragraph


    def filter_hasTag(self, item):
        if (item[3] == 'False'):
            return False
        else:
            return True

    # 集成过滤功能，输出的列表为可以上传的段落
    def filterOp_auto(self):
        paragraphList = self.getData()
        result = []
        for item in paragraphList:
            # 筛选有标签的
            if (self.filter_hasTag(item)):
                # 清序号
                item[1] = self.filter_delHeaderNum(item[1])
                # 清空格
                item[1] = self.filter_delSpace(item[1])
                # 清序号
                item[1] = self.filter_delHeaderNum(item[1])
                # 根据字符串长度125-250间进行筛选
                if(not self.filter_Between120to250(item[1])):
                    # 段落字数再125-250间，有用可传
                    continue
                result.append(
                    (
                        item[1],  # 段落内容
                        self.getTagFromDatabase(item[2])     # 段落关键词
                    )
                )
            else:
                continue
        return result

class Poster:
    def __init__(self):
        self.topicNameList = ['gppz', 'pzgs', 'pzpt']
        pass

    def getCurDate(self):
        return time.strftime("%Y%m%d", time.localtime())

    # 上传单个数据列表的方法
    def poster(self, item, interface='http://121.40.187.51:8088/api/key_paragraph_api'):
        userName = 'qin'
        password = 'qin123456'
        curDate = str(self.getCurDate())
        key = hashlib.md5(('datapool' + userName + password + curDate).encode('utf-8')).hexdigest()
        # 这里传文件的时候用绝对路径传，不然传了之后显示不了
        formData = ({
            "key": key,
            "account": userName,
            "password": password,
            'content': item[0],
            'keyword': item[1],
            'rekeyword': '配资'
        })
        m = MultipartEncoder(formData)
        headers2 = {
            "Content-Type": m.content_type
        }
        paragraphPostResult = requests.post(url=interface, data=m, headers=headers2)
        return paragraphPostResult


    def post_auto(self):
        for topicName in self.topicNameList:
            filterOpInstance = GetPostableData(topicName)
            effecticeData = filterOpInstance.filterOp_auto()
            for item in effecticeData:
                self.poster(item)


