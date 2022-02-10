import json
import scrapy
from fake_useragent import UserAgent
import bs4
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class WlstockSpider(scrapy.Spider):
    name = 'wlstockSpider'
    start_urls = 'https://www.wlstock.com/HuDong/BBSTopic_GetIndexList.aspx'

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
        'Referer': 'https://www.wlstock.com/WLCombat/WLCombatArticleList.aspx',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def start_requests(self):
        for i in range(1, 200):
            self.headers['User-Agent'] = str(UserAgent().random)
            body_data = 'pageIndex={}&pageSize=20'.format(str(i))
            yield scrapy.Request(self.start_urls, headers=self.headers, cookies=self.cookies, body=body_data, method='Post',callback=self.parse_list)

    def parse_list(self, response):
        data_lis = json.loads(json.loads(response.text)['Data'])
        commentItem = items.CommentItem()
        for i in data_lis:
            comment = i['Title']
            publishTime = i['CreatedDate2']
            commentItem['comment'] = comment
            commentItem['publishTime'] = publishTime.replace('月','').replace('日','')
            yield commentItem







