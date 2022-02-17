import json
import scrapy
from fake_useragent import UserAgent
import bs4
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class WlstockGupiaoSpider(scrapy.Spider):
    name = 'wlstockGupiaoSpider'
    start_urls = 'https://www.wlstock.com/chaogu/getspechalist.aspx'

    cookies = {
        'HWWAFSESID':'34526d0f749173f92d',
        'HWWAFSESTIME':'1644218103245',
        'ASP.NET_SessionId':'5y2ljhkddwl23zdrpvh2cszu',
        'Hm_lvt_16ae844519b6d6a721828d6914c625ff':'1644218107',
        '__utma':'1.1261066338.1644218125.1644218125.1644218125.1',
        '__utmc':'1',
        '__utmz':'1.1644218125.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        'AttentionStockNos':',002441,603126',
        '__utmt':'1',
        'Hm_lpvt_16ae844519b6d6a721828d6914c625ff':'1644219904',
        '__utmb':'1.28.10.1644218125'
    }
    headers = {
        'Host': 'www.wlstock.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.wlstock.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.wlstock.com/chaogu/index.aspx',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        body_data = 'channel=007005&pagesize=24&pageindex=1'
        yield scrapy.Request(self.start_urls, headers=self.headers, cookies=self.cookies, body=body_data, method='Post',callback=self.parse_articleList)

    def parse_articleList(self, response):
        articleinfo_lis = json.loads(json.loads(response.text)['Data'])
        url_list =[]
        for article in articleinfo_lis:
            publish_time = article['Date']
            url = article['FullUrl']
            title = article['Title']
            if(publish_time == Contraler_Time.getCurDate('%Y-%m-%d')):
                    url_list.append((title, url))
        for url in url_list:
            if (Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="article-bd-text"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in p_lis:
            paragraph = p.xpath('string()').extract_first().replace(' ', '').replace('\n','').replace('\t','').replace('\u3000','')
            if (
                '本文作者' in paragraph or '来源' in paragraph or '原文标题' in paragraph or '风险提示：' in paragraph or '以上内容' in paragraph
            ):
                continue
            if(paragraph):
                c = cleaner_paragraph.integratedOp(paragraph)
                content = content + '<p>' + c + '</p>'
            try:
                has_img = p.find('img')
            except Exception as e:
                has_img = False
            if(has_img):
                content = content + '<img src = \'' + has_img.get('src') + '\' />'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem






