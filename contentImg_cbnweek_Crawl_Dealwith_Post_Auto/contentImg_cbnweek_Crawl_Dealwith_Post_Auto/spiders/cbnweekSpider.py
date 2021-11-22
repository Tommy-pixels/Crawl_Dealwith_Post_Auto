from .. import tools, items
import json
import scrapy
from fake_useragent import UserAgent

class CbnweekSpider(scrapy.Spider):
    name = 'cbnweekSpider'
    headerStr = '''
        Host: www.cbnweek.com
        Connection: keep-alive
        sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
        Accept: application/json, text/plain, */*
        X-Signature: NzMyMjA4MTk0M2ZlYzQ3MzUzMTU5NDNjYWRhNGQxMzU=
        sec-ch-ua-mobile: ?0
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
        Sec-Fetch-Site: same-origin
        Sec-Fetch-Mode: cors
        Sec-Fetch-Dest: empty
        Referer: https://www.cbnweek.com/
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9
    '''
    cookieStr = 'UM_distinctid=17cc4972678da-04e8303632040d-6373264-1fa400-17cc4972679c1c; gr_user_id=b1c5a965-7113-45b7-97b4-8039ac4d2273; gr_session_id_98f39e7f937ee82d=1c154c2a-ca69-4ddb-8667-07468610dcaf; gr_session_id_98f39e7f937ee82d_1c154c2a-ca69-4ddb-8667-07468610dcaf=true; _ga=GA1.2.1688496522.1635399299; _gid=GA1.2.1498520175.1635399299; CNZZDATA1279846434=1166535525-1635319108-null%7C1635395843'
    page = 1
    encoder = tools.Encode()
    message = '64925f300924b0OzZRpXXz5CqIficrntbhjxmb8{}CBNWeeklyAPI'

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
        url = 'https://www.cbnweek.com/v4/first_page_infos?per=8&page=' + str(self.page)
        yield scrapy.Request(url=url, callback=self.parse_article, headers=self.header, cookies=self.cookie)

    def parse_article(self, response):
        dataList = json.loads(response.text)['data']
        imgItem = items.ImgItem()
        for articleInfo in dataList:
            coverImgUrl = articleInfo['data'][0]['cover_url']  # 封面图片链接
            imgItem['imgUrl'] = coverImgUrl
            imgItem['from_url'] = response.url
            yield imgItem
        self.page = self.page + 1
        self.header['X-Signature'] = self.encoder.encode0(self.message.format(self.page))
        self.header['User-Agent'] = str(UserAgent().random)
        url = 'https://www.cbnweek.com/v4/first_page_infos?per=8&page=' + str(self.page)
        while (self.page <= 1):
            yield scrapy.Request(url, callback=self.parse_article, headers=self.header, cookies=self.cookie)


