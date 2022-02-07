import scrapy
from fake_useragent import UserAgent
import time
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from bs4 import BeautifulSoup

def getCurDate(formatStr: str):
    return time.strftime(formatStr, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d')
    return time.mktime(b)

def clean_space(s):
    return s.replace('\t','').replace('\n','').replace('\u3000','').replace('\r','').replace(' ','')

class StockjrjSpider(scrapy.Spider):
    name = 'stockjrjSpider'
    start_url = [
        # 'http://stock.jrj.com.cn/list/stockgszx.shtml',
        'http://stock.jrj.com/list/stockssgs.shtml'
    ]
    cookies = {
        'UM_distinctid':'17e8abf3c03bdb-06f02e424f7177-6373264-1fa400-17e8abf3c045f8',
        'CNZZDATA1275542922':'1106552261-1643000345-http%253A%252F%252Fstock.jrj.com.cn%252F%7C1643000345',
        'WT_FPC':'id=2cc97ea45e6b6cab5521643005295598:lv=1643005858540:ss=1643005295598',
        'Hm_lvt_1d0c58faa95e2f029024e79565404408':'1643005296,1643005835,1643005859',
        'Hm_lpvt_1d0c58faa95e2f029024e79565404408':'1643005859',
        'Hm_lvt_4fef59384587fd0616a112c9f342bdd9':'1643005296,1643005835,1643005859',
        'Hm_lpvt_4fef59384587fd0616a112c9f342bdd9':'1643005859'
    }
    headers = {
        'Host': 'stock.jrj.com',
        'Connection': 'close',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://stock.jrj.com.cn/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }


    def start_requests(self):
        for url in self.start_url:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse_articleInfo)

    def parse_articleInfo(self,response):
        article_lis = response.xpath('//div[@class="list-main"]/ul/li[not(@class)]')
        yesterday = int(getSecondByDate(getCurDate('%Y-%m-%d')))
        curTime = int(round(time.time()))
        url_lis = []
        for article in article_lis:
            url = article.xpath('./a/@href').extract_first()
            publishTime = article.xpath('./span/text()').extract_first().split('  ')[0]
            # if(int(getSecondByDate(publishTime))<yesterday):
            #     break
            if(int(getSecondByDate(publishTime))>=yesterday):
                if(url not in url_lis):
                    url_lis.append(url)
        for url in url_lis:
            self.headers['User-Agent'] = str(UserAgent().random)
            self.headers['Host'] = 'stock.jrj.com.cn'
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        title = response.xpath('//h1').xpath('string(.)').extract_first()
        content = ''
        p_div = response.xpath('//div[@class="texttit_m1"]/*')
        cleaner_paragraph = Cleaner_Paragraph()
        # b = BeautifulSoup(response.text)
        # b.find(attrs={'class': 'texttit_m1'}).text
        for p in p_div:
            try:
                imgs = p.xpath('.//img/@href').extract()
                c = clean_space(p.xpath('./text()').extract_first())
                if(c):
                    c = cleaner_paragraph.integratedOp(c)
                    content = content + '<p>' + c + '</p>'
                if(imgs):
                    for img in imgs:
                        content = content + '<img src=\'' + img + '\' />'
            except Exception as e:
                print(p)
        articleItem = items.ArticleContentItem()
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem

