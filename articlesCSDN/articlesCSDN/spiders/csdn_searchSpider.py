import scrapy, time
from fake_useragent import UserAgent
from .. import items
import json


class HexunSpider(scrapy.Spider):
    name = 'csdnSpider'
    start_url = 'https://so.csdn.net/api/v3/search?q=%E6%8E%A5%E5%8F%A3&t=all&p={}&s=0&tm=365&lv=4&ft=0&l=&u=&ct=-1&pnt=-1&ry=-1&ss=-1&dct=-1&vco=-1&cc=-1&sc=-1&akt=-1&art=-1&ca=-1&prs=&pre=&ecc=-1&ebc=-1&ia=1&cl=-1&scl=-1&tcl=-1&platform=pc'
    headers = {
        'Host': 'so.csdn.net',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&s=0&lv=4&tm=365',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {

        }

    def start_requests(self):
        for i in range(0, 21):
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)
            time.sleep(1)

    def parse_articleInfo(self, response):
        li_lis = json.loads(response.text)['result_vos']
        article_info_item = items.ArticleItem()
        for article in li_lis:
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

