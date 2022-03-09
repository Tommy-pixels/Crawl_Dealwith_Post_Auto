import scrapy, time
from fake_useragent import UserAgent
from .. import items
import json


class HexunSpider(scrapy.Spider):
    name = 'csdn21Spider'

    start_url = 'https://gsp0.baidu.com/yrwHcjSl0MgCo2Kml5_Y_D3/api/customsearch/apisearch?s=10742016945123576423&q=%E6%8E%A5%E5%8F%A3&nojc=1&ct=2&cc=blog.csdn.net%2526download.csdn.net%2526bbs.csdn.net%2526edu.csdn.net%2526ask.csdn.net%2526www.csdn.net&p={}&tk=5ff687f1302e609d08e92386af91fb15&v=2.0&callback=flyjsonp_65F942B36B1C42E0805B5C40A8866ED5'
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
        'BAIDUID_BFESS':'D11DFE78E46F31A3502F00DA11FBF293:FG=1'
    }
    def start_requests(self):
        for i in range(0, 50):
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

    # def parse_content(self, response):
    #     articleContentItem = items.ArticleContentItem()
    #     title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
    #     pList = response.xpath('//div[@class="art_contextBox"]/p')
    #     content = ''
    #     cleaner_paragraph = Cleaner_Paragraph()
    #     for p in pList:
    #         c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '')
    #         if ('扫描下方二维码' in c or '商报记者' in c or '点击查看' in c):
    #             break
    #         if (c != '' and '中新经纬摄' not in c and '来源：' not in c and '仅供参考' not in c and '编辑：' not in c
    #                 and '记者：' not in c and '声明：' not in c and '排版：' not in c and '视觉：' not in c and '封面：' not in c and '整理：' not in c
    #                 and '打开APP 阅读最新报道' not in c and '转载请注明' not in c and '责任编辑' not in c and '作者：'not in c and '附表：' not in c and '（作者' not in c
    #         ):
    #             c = cleaner_paragraph.integratedOp(c)
    #             if(int(len(c))<3):
    #                 pass
    #             else:
    #                 content = content + '<p>' + c + '</p>'
    #         if (p.xpath('.//img') != []):
    #             for img in p.xpath(".//img"):
    #                 content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'
    #
    #     articleContentItem['title'] = title
    #     articleContentItem['content'] = content
    #     yield articleContentItem

