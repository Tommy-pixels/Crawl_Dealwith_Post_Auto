import scrapy
from fake_useragent import UserAgent
import time
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph

def getCurDate(formatStr: str):
    return time.strftime(formatStr, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d')
    return time.mktime(b)

def clean_space(s):
    return s.replace('\t','').replace('\n','').replace('\u3000','').replace('\r','').replace(' ','')

class Yingjia360Spider(scrapy.Spider):
    name = 'yingjia360Spider'
    start_url = 'http://www.yingjia360.com/'


    cookies = {
        'Hm_lvt_370e77bee1980c4d3dbde0d98c438fe1':'1642727177',
        'UM_distinctid':'17e7a2b7c1e2c2-0ce6a8ec2fa32e-6373264-1fa400-17e7a2b7c1fc91',
        'CNZZDATA1000318254':'1445306769-1642718843-null%7C1642718843; _ga=GA1.2.1190067360.1642727178',
        '_gid':'GA1.2.1463739533.1642727178',
        'ib_vid':'5ba1a2877349a7ff4e818daddb635aa1',
        'Hm_lpvt_370e77bee1980c4d3dbde0d98c438fe1':'1642729183'
    }
    headers = {
        'Host': 'www.yingjia360.com',
        'Connection': 'close',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://www.yingjia360.com/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }


    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        yield scrapy.Request(url=self.start_url, cookies=self.cookies, headers=self.headers, callback=self.parse_temp)

    def parse_temp(self,response):
        theNewestArticles = response.xpath('//div[@id="zuixinde"]/a/@href').extract()
        for url in theNewestArticles:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse_articleInfo)

    def parse_articleInfo(self,response):
        uldiv_lis = response.xpath('//div[@class="paihang clearfix"]//div[@class="paihang_nr"]')
        uldiv_lis.pop(1)
        uldiv_lis.pop(1)
        article_lis = []
        yesterday = int(getSecondByDate(getCurDate('%Y-%m-%d')))
        curTime = int(round(time.time()))
        for uldiv in uldiv_lis:
            li_lis = uldiv.xpath('.//ul/li')
            for li in li_lis:
                url = li.xpath('.//a/@href').extract_first()
                publishTime = li.xpath('.//span[@class="r"]/text()').extract_first()
                if(int(getSecondByDate(publishTime))>=yesterday):
                    if(url not in article_lis):
                        article_lis.append(url)
        for url in article_lis:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse_content, dont_filter=True)

    def parse_content(self, response):
        title = response.xpath('//h1/text()').extract_first()
        content = ''
        publishTime = response.xpath('//div[@class="title_from"]/span')[-1].xpath('./text()').extract_first().replace('添加时间：', '').split(' ')[0]
        publishTime = int(getSecondByDate(publishTime))
        yesterday = int(getSecondByDate(getCurDate('%Y-%m-%d')))-3600*24
        if(publishTime>yesterday):
            p_div = response.xpath('//div[@class="art_nr"]/*')
            text_temp_lis = response.xpath('//div[@class="art_nr"]//text()').extract()
            text_lis = []
            for i in text_temp_lis:
                s = clean_space(i)
                if(s!=''):
                    text_lis.append(s)
            text_temp_lis = []
            text_temp_lis.append(''.join(text_lis[0:3]))
            for i in text_lis[3:]:
                text_temp_lis.append(i)
            text_lis = text_temp_lis
            imgs_lis = []
            for i in p_div:
                img = i.xpath('.//img/@src').extract()
                if(img):
                    imgs_lis.extend(i.xpath('.//img/@src').extract())
            cleaner_paragraph = Cleaner_Paragraph()
            for c in text_lis:
                if (
                    'QQ' in c or
                    '讲解更多' in c or
                    '关注赢家财富网' in c or
                    '进行咨询' in c or
                    'function' in c or
                    '来源于' in c or
                    '江恩软件' in c or
                    '点击进入' in c
                ):
                    break
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
                if(imgs_lis):
                    content = content + '<img src=\'' + imgs_lis[0] + '\' />'
                    imgs_lis.pop(0)
        articleItem = items.ArticleContentItem()
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem

