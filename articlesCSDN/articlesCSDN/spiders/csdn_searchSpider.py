import scrapy, time
from fake_useragent import UserAgent
from .. import items
import json


class CSDNSpider(scrapy.Spider):
    name = 'csdnSpider'
    '''
    vip文章 vco=1
    '''
    start_url = 'https://so.csdn.net/api/v3/search?q=%E8%82%A1%E7%A5%A8%E6%8E%A5%E5%8F%A3&t=all&p={}&s=0&tm={}&lv={}&ft=0&l=&u=&ct=-1&pnt=-1&ry=-1&ss=-1&dct=-1&vco=1&cc=-1&sc=-1&akt=-1&art=-1&ca=-1&prs=&pre=&ecc=-1&ebc=-1&ia=1&cl=-1&scl=-1&tcl=-1&platform=pc'
    headers = {
        'Host': 'so.csdn.net',
        'Connection': 'close',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&s=0&lv={}&tm={}',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = {
        'uuid_tt_dd':'10_19005485070-1648522122440-983838',
        'dc_session_id':'10_1648522122440.307247',
        'dc_sid':'61bfa959f0dc85e791ca3750ffd94ae5',
        'c_first_ref':'default',
        'c_first_page':'https://so.csdn.net/so/search%3Fspm=1001.2101.3001.4501%26q%3D%25E8%2582%25A1%25E7%25A5%25A8%25E6%258E%25A5%25E5%258F%25A3%26t%3D%26u%3D%26vco%3D-1',
        'c_segment':'14',
        'Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac':'1648522125'
        }

    def start_requests(self):
        li_dic_lis = [
            # {'lv': '5', 'tm' : '0'},
            # {'lv': '3', 'tm': '7'},
            # {'lv': '3', 'tm': '30'},
            # {'lv': '3', 'tm': '90'},
            {'lv': '3', 'tm': '365'},
        ]
        for dic in li_dic_lis:
            for i in range(1, 2):
                self.headers['Referer'] = 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&vco=1&s=0&lv={}&tm={}'.format(dic['lv'], dic['tm'])
                self.headers['User-Agent'] = str(UserAgent().random)
                yield scrapy.Request(url=self.start_url.format(str(i), dic['tm'], dic['lv']), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)
                time.sleep(5)

    def parse_articleInfo(self, response):
        li_lis = json.loads(response.text)['result_vos']
        article_info_item = items.ArticleItem()
        for article in li_lis:
            article_type = article['type']
            if(article_type=='ebookchapter_new'):
                continue
            # article_id = article['articleid']
            title = article['title']
            create_time = article['created_at']
            author = article['author']
            url = article['url']
            crawl_time = time.strftime('%Y-%m-%d %H:%M:%S')
            article_info_item['title'] = title
            # article_info_item['article_id'] = article_id
            article_info_item['create_time'] = create_time
            article_info_item['author'] = author
            article_info_item['url'] = url
            article_info_item['crawl_time'] = crawl_time
            yield article_info_item

