import scrapy
from fake_useragent import UserAgent
from .. import items

class AitouyanSpider(scrapy.Spider):
    name = 'aitouyanSpider'
    start_url = 'https://www.aitouyan.com/gpjczs/p-{}/'
    headers = {
        'Host': 'www.aitouyan.com',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.aitouyan.com/gpjczs',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'UM_distinctid':'17ddfe7721c305-03422dbd30f0cb-6373264-1fa400-17ddfe7721df47',
        'CNZZDATA1280224203':'442729480-1640136197-%7C1640136197',
        'Hm_lvt_51e2b8a34c49f9abed9d1033ded59c5f':'1640139027',
        'koa.sessxx':'82e92b4cb2d3c7707c415d12146d50e72df94c9af8b8dee4',
        'Hm_lpvt_51e2b8a34c49f9abed9d1033ded59c5f':'1640139164'
    }

    def start_requests(self):
        for i in range(6):
            self.headers['User-Agent'] = str(UserAgent().random)
            if(i==1):
                self.headers['Referer'] = 'https://www.aitouyan.com/gupiaozhishi/'
            else:
                self.headers['Referer'] = 'https://www.aitouyan.com/gupiaozhishi/p-{}/'.format(str(i-1))
            yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        url_lis = []
        li_lis = response.xpath('//div[@class="article_list"]/ul/li')
        for li in li_lis:
            publishTime = li.xpath('.//span[@class="fr"]/text()').extract_first()
            url = 'https://www.aitouyan.com' + li.xpath('.//h2/a/@href').extract_first()
            title = li.xpath('.//h2')[0].xpath('string(.)').extract_first()
            # classification = li.xpath('.//span[@class="fl"]').xpath('.//span[@class="fl"]/text()').extract_first().split('：')[1]
            # if(classification=='股票公式'):
            #     continue
            if('前' not in publishTime):
                continue
            if(url not in url_lis):
                url_lis.append(url)
        for article_url in url_lis:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=article_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleContent)

    def parse_articleContent(self, response):
        p_lis = response.xpath('//div[@class="main_text"]/p')
        paragraphItem = items.ParagraphItem()
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first()
            if(paragraph==''):
                continue
            paragraphItem['paragraph'] = paragraph
            paragraphItem['referArticleUrl'] = response.url
            yield paragraphItem