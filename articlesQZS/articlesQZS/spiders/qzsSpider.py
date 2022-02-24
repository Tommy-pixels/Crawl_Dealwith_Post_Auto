import scrapy
from fake_useragent import UserAgent
import time
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner



def getCurDate(formatStr: str):
    return time.strftime(formatStr, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    return time.mktime(b)

class QZSSpider(scrapy.Spider):
    name = 'qzsSpider'

    start_urls = 'https://qzs.stcn.com/yw/'

    cookies = {
        'qzsToken':'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyZWd1c2VyNjBAcXNjbiIsImlhdCI6MTY0NTY2NTEwMywiZXhwIjoxNjUwODQ5MTAzLCJhdXRoVHlwZSI6MH0.TJl8TJdNx5QkE46gj4AqYEi8OosI9UGfQj-o31U8zRA'
    }
    headers = {
        'Host': 'qzs.stcn.com',
        'Connection': 'close',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
		'Sec-Fetch-Mode': 'navigate',
		'Sec-Fetch-User': '?1',
		'Sec-Fetch-Dest': 'document'
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls, headers=self.headers, cookies=self.cookies, callback=self.parse_articleList)

    def parse_articleList(self, response):
        articleinfo_lis = response.xpath('//div[@class="news_list"]/div[@class="single_img clearfix"]')
        url_list =[]
        for article in articleinfo_lis:
            publish_time = article.xpath('./div[@class="fr single_right"]/a/@href').extract_first().split('/')[-1].split('_')[0]
            url = 'https://qzs.stcn.com' + article.xpath('./div[@class="fr single_right"]/a/@href').extract_first()[2:]
            title = article.xpath('./div[@class="fr single_right"]/a//span/text()').extract_first().replace('\n', '').replace('\t','').replace(' ','')
            if(getCurDate('%Y%m%d') in publish_time):
                url_list.append((title, url))
        if('天前' not in articleinfo_lis[-1].xpath('./div[@class="fr single_right"]/a/@href').extract_first().split('/')[-1].split('_')[0]):
            articleinfo_more_lis = response.xpath('//div[@class="news_list"]/ul[@class="pre_data"]/li')
            for li in articleinfo_more_lis:
                publish_time2 = li.extract().split('<url>')[-1].split('</url>')[0].split('/')[-1].split('_')[0]
                if(getCurDate('%Y%m%d') in publish_time2):
                    url_list.append((title, url))
                else:
                    continue
        for url in url_list:
            if (Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], cookies=self.cookies, headers=self.headers,callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="content_text"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        if(p_lis[-1].xpath('.//img') != []):
            p_lis = p_lis[:-1]
        elif(p_lis[-2].xpath('.//img') != []):
            p_lis = p_lis[:-2]
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first().replace(' ', '').replace('\n','').replace('\t','').replace(' ', '')
            if (
                '本报记者' in paragraph or '注：' in paragraph or '原文标题' in paragraph or '仅供参考' in paragraph or '数据来源：' in paragraph
                or '责编：' in paragraph or '【摘要】' in paragraph
            ):
                continue
            if(paragraph):
                c = Base_Cleaner.del_content_between(paragraph, s_left='（来源：', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）')
                if (c.startswith('，') or c.startswith(',')):
                    c = c[1:]
                c = cleaner_paragraph.integratedOp(c)
                if(int(len(c))<3):
                    pass
                else:
                    content = content + '<p>' + c.replace('券商中国', '') + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    if('.gif' not in imgsrc):
                        content = content + '<img src=\'' + 'https://qzs.stcn.com/gzh/' + getCurDate("%Y%m") + imgsrc[1:] + '\'/>'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem






