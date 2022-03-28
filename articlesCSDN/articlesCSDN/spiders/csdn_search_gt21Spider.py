import scrapy, time
from fake_useragent import UserAgent
from .. import items
import json


class CSDNSpider(scrapy.Spider):
    name = 'csdn21Spider'

    start_url = 'https://gsp0.baidu.com/yrwHcjSl0MgCo2Kml5_Y_D3/api/customsearch/apisearch?s=10742016945123576423&q=%E6%8E%A5%E5%8F%A3&nojc=1&ct=2&cc=blog.csdn.net%2526download.csdn.net%2526bbs.csdn.net%2526edu.csdn.net%2526ask.csdn.net%2526www.csdn.net&p={}&tk=5ff687f1302e609d08e92386af91fb15&v=2.0&callback=flyjsonp_F7E8D4DC4DD7411DB74055E9B8AEAA59'
    headers = {
        'Host': 'gsp0.baidu.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'Referer': 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&s=0&lv=5&tm=0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'BAIDUID_BFESS':'D458AC18B8D6743CBCF03D93C5C57D02:FG=1'
    }
    def start_requests(self):
        li_dic_lis = [
            # {'s':'new', 'lv': '5', 'tm' : '0'},
            # {'s':'new', 'lv': '5', 'tm': '7'},
            {'s':'new', 'lv': '5', 'tm': '30'},
            # {'s':'new', 'lv': '5', 'tm': '90'},
            # {'s':'new', 'lv': '5', 'tm': '365'},
        ]
        for dic in li_dic_lis:
            for i in range(0, 50):
                self.headers['Referer'] = 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&s={}&lv={}&tm={}'.format(dic['s'], dic['lv'], dic['tm'])
                self.headers['User-Agent'] = str(UserAgent().random)
                yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)
                time.sleep(5)

    def parse_articleInfo(self, response):
        li_lis = json.loads(response.text[42:-1])['blockData']
        article_info_item = items.ArticleItem()
        for article in li_lis:
            # article_id = article['articleid']
            title = article['title']
            create_time = article['timeshow']
            url = article['linkurl']
            crawl_time = time.strftime('%Y-%m-%d %H:%M:%S')
            article_info_item['title'] = title
            # article_info_item['article_id'] = article_id
            article_info_item['create_time'] = create_time
            article_info_item['url'] = url
            article_info_item['crawl_time'] = crawl_time
            yield article_info_item
        # for url in urlList:
        #     yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)


