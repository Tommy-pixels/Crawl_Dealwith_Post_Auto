import scrapy
import json, time
from ..tools import getSecondByFormat, randomSleep
from ..items import CommentItem, ArticleItem

class quote1Spider(scrapy.Spider):
    name = "comment1Spider"   # 存放淘股吧7*24讨论（https://www.taoguba.com.cn/quotes/）评论内容
    start_url = "https://www.taoguba.com.cn/quotes/hotDiscussion?groupID=0&pageNo={}"
    times = 1

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
    cookieStr = "acw_tc=0bde430616359884674927409e0141e395803eecc595be4f34b9665fa6e44b; JSESSIONID=fcdb4127-40bd-40da-8eba-3c0e38af158a; UM_distinctid=17ce882f718e2f-0f7dbe70040c49-6373264-1fa400-17ce882f719775; CNZZDATA1574657=cnzz_eid%3D1664214953-1635982895-%26ntime%3D1635982895; Hm_lvt_cc6a63a887a7d811c92b7cc41c441837=1635988470; Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837=1635988470; agree=enter"


    def start_requests(self):
        headerList = self.headerStr.split('\n')
        self.header = {}
        for headerItem in headerList:
            i = headerItem.strip().split(":")
            if (i != ['']):
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
        yield scrapy.Request(url=self.start_url.format(self.times), cookies=self.cookie, headers=self.header, callback=self.parse)


    def parse(self, response):
        dto = json.loads(response.text)['dto']
        dataList = dto['hotDiscussion']
        for data in dataList:
            rid = data['rID']
            articleUrl = 'https://www.taoguba.com.cn/Article/{}/1'.format(rid)
            yield scrapy.Request(url=articleUrl, callback=self.parse_article)
            randomSleep(5)

    def parse_article(self, response):
        lis = response.xpath("//div[@id='new_wrap_container']//div[contains(@class, 'pc_p_nr')]")
        commentItem = CommentItem()
        for i in lis:
            if('reply_' not in i.xpath(".//@id").extract_first()):
                continue
            comment = i.xpath(".//div[@class='pcnr_wz']").xpath("string()").extract_first().strip()
            if('#' in comment or '$' in comment or '@' in comment):
                continue
            publishTime = i.xpath(".//div[@class='pc_yc_an']//div[@class='left pcyc_l']/span")[-1].xpath("string()").extract_first().strip() + ":00"
            publishTime = getSecondByFormat(publishTime, formatStr='%Y-%m-%d %H:%M:%S') * 1000
            commentItem['comment'] = comment
            commentItem['publishTime'] = publishTime
            yield commentItem
        if(self.times<5):
            self.times = self.times + 1
            yield scrapy.Request(url=self.start_url.format(self.times), cookies=self.cookie, headers=self.header, callback=self.parse)
            randomSleep(10)


    def close(spider, reason):
        print("爬虫结束")