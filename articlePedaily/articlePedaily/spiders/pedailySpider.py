import scrapy, time
from .. import items
from fake_useragent import UserAgent
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d %H:%M')
    return time.mktime(b)

def getMilliSecond():
    return int(round(time.time()))

class PedailySpider(scrapy.Spider):
    name = 'pedailySpider'
    start_urls = 'https://www.pedaily.cn/all/'

    headers = {
        'Host': 'www.pedaily.cn',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json;charset=utf-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.pedaily.cn/all',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = {
        '__uid':'1470768164 ',
        '__fromtype':'0',
        'Hm_lvt_25919c38fb62b67cfb40d17ce3348508':'1640826812',
        'BAIDU_SSP_lcr':'https://www.lieyunwang.com/',
        '__utmc':'23980325',
        '__utmz':'23980325.1640826812.1.1.utmcsr=lieyunwang.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
        '__utma':'23980325.1834321668.1640826812.1640826812.1640831031.2',
        '__utmt':'1',
        'accesstoken':'LT05DRVNIS',
        'Hm_lpvt_25919c38fb62b67cfb40d17ce3348508':'1640831205',
        '__utmb':'23980325.16.10.1640831031'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls ,
            headers=self.headers,
            cookies=self.cookies,
            callback=self.article_info,
        )

    def article_info(self, response):
        datalis = response.xpath('//ul[@id="newslist-all"]/li')
        articlelis = []
        for article in datalis:
            title = article.xpath('.//h3/a/text()').extract_first()
            article_url = article.xpath('.//h3/a/@href').extract_first()
            publish_time = article.xpath('.//div[@class="tag"]/span[@class="date"]/text()').extract_first()
            if(int(getSecondByDate(publish_time)) > getMilliSecond()-3600*3):
                articlelis.append((title, article_url))
        cb_p = {}
        for article_url in articlelis:
            if (Base_Identifier.is_intterrogative(article_url[0])):
                cb_p['title'] = article_url[0]
                self.headers['Host'] = 'news.pedaily.cn'
                self.headers['User-Agent'] = str(UserAgent().random)
                yield scrapy.Request(
                    url=article_url[1],
                    headers=self.headers,
                    cookies=self.cookies,
                    callback=self.article_content,
                    cb_kwargs=cb_p
                )

    def article_content(self, response, title):
        content = ''
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath("//div[@id='news-content']/p")
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = "".join(p.xpath('string(.)').extract())
            if('参考资料' in c):
                break
            if(c!='' and '投资界原创' not in c):
                c = cleaner_paragraph.integratedOp(c)
                content = content + "<p>" + c + "</p>"
            if(p.xpath('.//img')!=[]):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'' + imgsrc + '\'/>'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


