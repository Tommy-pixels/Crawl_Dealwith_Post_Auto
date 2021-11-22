import scrapy
import json
from ..items import CommentItem
from ..tools import DBConnector, getCurDate, getSecondByDate, getSecond, randomSleep

class quote1Spider(scrapy.Spider):
    name = "comment2Spider"   # 存放淘股吧首页（https://www.taoguba.com.cn/） Tab淘县神评下内容

    start_url_head = "https://www.taoguba.com.cn/newIndex/getReplySP?pageNo="
    num = 1
    start_url_tail = "&type=ALL"

    headerStr = """
        Host: www.taoguba.com.cn
        Connection: keep-alive
        sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
        Accept: */*
        X-Requested-With: XMLHttpRequest
        sec-ch-ua-mobile: ?0
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
        Sec-Fetch-Site: same-origin
        Sec-Fetch-Mode: cors
        Sec-Fetch-Dest: empty
        Referer: https://www.taoguba.com.cn/
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9
    """
    cookieStr = "agree=enter; Hm_lvt_cc6a63a887a7d811c92b7cc41c441837=1634524932,1634525393,1634534717; CNZZDATA1574657=cnzz_eid%3D1028541325-1634524322-https%253A%252F%252Fwww.baidu.com%252F%26ntime%3D1634535122; UM_distinctid=160341f651719b-0a2862; acw_tc=0bcb865f16345428192525448ee2cf07efec3fdc854fbde6d2ef9ddc6b0c98; JSESSIONID=2d5799a8-0dbf-4ff3-93bf-4bdfc1754d8a; Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837=1634543502"

    def start_requests(self):
        headerList = self.headerStr.split('\n')
        self.header = {}
        for headerItem in headerList:
            i = headerItem.strip().split(":")
            if(i!=['']):
                k = i[0]
                v = i[1]
                self.header[k] = v
        cookieList = self.cookieStr.split(";")
        self.cookie = {}
        for cookieItem in cookieList:
            i = cookieItem.strip().split("=")
            k = i[0]
            v = i[1]
            self.cookie[k] = v
        yield scrapy.Request(url=self.start_url_head+"1"+self.start_url_tail, cookies=self.cookie, headers=self.header, callback=self.parse)
        randomSleep(10)

    def parse(self, response):
        print(response.url)
        datalis = json.loads(response.text)['dto']['list']
        print(len(datalis))
        commentItem = CommentItem()
        dbConnector = DBConnector()
        sqlGet = "SELECT * FROM commentdatabase.tb_newestseconds WHERE (`id` = '1');"
        theNewestSecond = dbConnector.getOneSQL(sqlGet)[1]
        curDateSecond = int(getSecondByDate(getCurDate())*1000)
        for data in datalis:
            content = data['content']
            publishTime = data['postDate']
            if(theNewestSecond!=''):
                if(int(publishTime)<int(theNewestSecond) and int(publishTime)>curDateSecond):
                    continue
            elif('#' in content or '$' in content or '@' in content):
                continue
            commentItem['comment'] = content
            commentItem['publishTime'] = publishTime
            yield commentItem
        # 爬取到的最小时间戳
        minSeconds = datalis[-1]['postDate']
        print("minSeconds", minSeconds)
        sqlUpdate = "UPDATE `commentdatabase`.`tb_newestseconds` SET `seconds` = '" + str(minSeconds) + "', `insert_seconds` = '" + str(getSecond()) + "' WHERE (`id` = '1');"
        dbConnector.updateSQL(sqlUpdate)  # 更新操作
        if(datalis[-2]['postDate']>getSecondByDate(getCurDate())*1000):
        # if (self.num <5):
            self.num = self.num + 1
            # 当天的评论还没完
            yield scrapy.Request(url=self.start_url_head+str(self.num)+self.start_url_tail, headers=self.header, cookies=self.cookie, callback=self.parse)
            randomSleep(10)



