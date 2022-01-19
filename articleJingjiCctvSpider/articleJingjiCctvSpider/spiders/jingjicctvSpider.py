import json, re
import scrapy, time
from .. import items
from fake_useragent import UserAgent
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier

def del_brackets(s, sl,sr):
    r_rule = u"\\" + sl + u".*?" + sr
    return re.sub(r_rule, "", s)

def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    return time.mktime(b)

def getMilliSecond():
    return int(round(time.time()))

class CctvJingjiSpider(scrapy.Spider):
    name = 'cctvJingjiSpider'
    start_urls = 'https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/economy_zixun_1.jsonp'

    headers = {
        'Host': 'news.cctv.com',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json;charset=utf-8',
        'Sec-Fetch-Site': ' cross-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://jingji.cctv.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = {
        'cna':'mENVGrkeXnMCAQphgf63UB5p',
        'sca':'b84a1e9f',
        'atpsida':'c36d0e12259f92ade0b25b6f_1640913211_7'
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls,
            headers=self.headers,
            cookies=self.cookies,
            callback=self.article_info,
        )

    def article_info(self, response):
        datalis = json.loads(response.text[:-1].replace('economy_zixun(', ''))['data']['list']
        articlelis = []
        for article in datalis:
            title = article['title']
            article_url = article['url']
            publish_time = article['focus_date']
            if(int(getSecondByDate(publish_time)) > getMilliSecond()-3600*5):
                articlelis.append((title, article_url))
        cb_p = {}
        for article_url in articlelis:
            if (Base_Identifier.is_intterrogative(article_url[0])):
                cb_p['title'] = article_url[0]
                self.headers['Host'] = 'jingji.cctv.com'
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
        pList = response.xpath("//div[@class='content_area']/*")
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = "".join(p.xpath('string(.)').extract()).replace('\u3000', '').replace('\n', '')
            if(c!='' and '本报记者' not in c and '见习记者 ' not in c and '记者 ' not in c):
                if('央视网消息' in c or '本报讯' in c):
                    c = c.replace('央视网消息', '').replace('本报讯', '')
                c = del_brackets(c, sl='（记者', sr='）')
                if (content.startswith('：') or content.startswith(':')):
                    content = content[1:]
                c = cleaner_paragraph.integratedOp(c)
                content = content + "<p>" + c + "</p>"
            if(p.xpath('.//img')!=[]):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'https:' + imgsrc + '\'/>'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


