import pymysql
import os, time, requests, hashlib
from requests_toolbelt import MultipartEncoder

"""
    一个处理所有段落的类
    判断段落中是否含有指定关键字，含有则返回对应的段落和关键字
"""
class getParagraphFromMysql():
    def __init__(self):
        self.sql = "select * from `nanfangcaifudatabase`.`tb_articlecontent`;"
        self.keywordList = [
            '个股', '股市', 'A股', '港股', '新股', '美股', '创业板', '证券股', '股票', '炒股', '散户', '短线', '操盘', '波段'
        ]
        self.connect()
        self.paragraphsList = self.get_Paragraphs()
        self.close()

    def connect(self):
        self.conn = pymysql.connect(
            host='localhost',
            user="root",
            passwd="root",
            db="nanfangcaifudatabase",
            autocommit=True
        )
        self.cursor = self.conn.cursor()
        pass

    def get_Paragraphs(self):
        self.cursor.execute(self.sql)
        result = self.cursor.fetchall()
        return result

    def checkParagraph_ByKeyword(self, paragraph, keyword):
        if(keyword in paragraph and len(paragraph)>=125 and len(paragraph)<=250):
            # 关键字存在而且段落字数符合要求返回True
            return True
        else:
            return False

    def checkPList_ByKeyword(self, keyword):
        pList = []
        for item in self.paragraphsList:
            if(self.checkParagraph_ByKeyword(paragraph=item[2], keyword=keyword)):
                pList.append((item[2], keyword))
        return pList

    def close(self):
        self.cursor.close()
        self.conn.close()

class sendRelateParagraph():
    # paragraphList是符合要求的段落列表，列表包含关键字以及对应的段落
    def __init__(self):
        self.keywordList = [
            '个股', '股市', 'A股', '港股', '新股', '美股', '创业板', '证券股', '股票', '炒股', '散户', '短线', '操盘', '波段'
        ]
        # self.paragraphList = paragraphList
        self.post_auto()

    def getCurDate(self):
        return time.strftime("%Y%m%d", time.localtime())

    # item 格式规范如右边 ('段落', '对应的关键字')
    def post_paragraphSingle(self, item, interface='http://121.40.187.51:8033/api/relation_paragraph_api'):
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
            'keyword': item[1]
        })
        m = MultipartEncoder(formData)
        headers2 = {
            "Content-Type": m.content_type
        }
        paragraphPostResult = requests.post(url=interface, data=m, headers=headers2)
        return paragraphPostResult

    def post_auto(self):
        getter = getParagraphFromMysql()
        for keyword in self.keywordList:
            paragraphList = getter.checkPList_ByKeyword(keyword=keyword)
            for item in paragraphList:
                self.post_paragraphSingle(item)