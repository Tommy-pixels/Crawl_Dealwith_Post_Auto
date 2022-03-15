import scrapy
import json, time
from ..tools import getSecondByFormat, randomSleep
from ..items import CommentItem
from fake_useragent import UserAgent

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
    cookieStr = "acw_tc=0bde430616359884674927409e0141e395803eecc595be4f34b9665fa6e44b; JSESSIONID=fcdb4127-40bd-40da-8eba-3c0e38af158aJSESSIONID=95ccef99-e071-4a27-af6f-018ff1695f13; UM_distinctid=17f8b5a51a6119-067ab594e3587a-6373264-1fa400-17f8b5a51a7ebd; Hm_lvt_cc6a63a887a7d811c92b7cc41c441837=1647308437; Hm_lpvt_cc6a63a887a7d811c92b7cc41c441837=1647310427; CNZZDATA1574657=cnzz_eid%3D1913154371-1647300210-https%253A%252F%252Fcn.bing.com%252F%26ntime%3D1647300210"


    def start_requests(self):
        headerList = self.headerStr.split('\n')
        self.header = {}
        for headerItem in headerList:
            i = headerItem.strip().split(":")
            if (i != ['']):
                k = i[0]
                v = i[1]
                self.header[k] = v
        self.header['User-Agent'] = UserAgent().random
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
            comment_lis = i.xpath(".//div[@class='pcnr_wz']/*")
            if(len(comment_lis)==2):
                comment = comment_lis[0].xpath("string()").extract_first().strip().replace('\n','').replace(' ','')
            else:
                comment = comment_lis.xpath("string()").extract_first().strip().replace('\n', '').replace(' ', '')
            if('#' in comment or '$' in comment or '@' in comment):
                a_tag_str_lis = i.xpath(".//div[@class='pcnr_wz']//a")
                for li in a_tag_str_lis:
                    comment = comment.replace(li.xpath("string()").extract_first().strip(), '')
            if(comment.startswith(':') or comment.startswith('：') or comment.startswith('，') or comment.startswith(',')):
                comment = comment[1:]
            t_lis = ['～']
            for m in t_lis:
                comment = comment.replace(m,' ')
            publishTime = i.xpath(".//div[@class='user-data-time left']/span")[-1].xpath("string()").extract_first().strip() + ":00"
            publishTime = getSecondByFormat(publishTime, formatStr='%Y-%m-%d %H:%M:%S') * 1000
            commentItem['comment'] = comment
            commentItem['publishTime'] = publishTime
            yield commentItem



        if(self.times<10):
            self.times = self.times + 1
            yield scrapy.Request(url=self.start_url.format(self.times), cookies=self.cookie, headers=self.header, callback=self.parse)
            randomSleep(10)


    def close(spider, reason):
        print("爬虫结束")