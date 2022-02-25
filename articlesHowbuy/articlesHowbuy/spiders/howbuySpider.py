import scrapy
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class HowbuySpider(scrapy.Spider):
    name = 'howbuySpider'
    start_urls = 'https://simu.howbuy.com/xinwen/smjd/list.htm'
    cookies = {
        '__hutma':'268394641.910991063.1645765789.1645765789.1645765789.1',
        '__hutmz':'268394641.1645765789.1.1.hutmcsr=(direct)|hutmccn=(direct)|hutmcmd=(none)',
        '__hutmc':'268394641',
        '__hutmmobile':'13CE04DB-E0A8-4600-977B-3D1301D5686D',
        'Hm_lvt_f737b389ea57a0a21e1ff802f849fbf0':'1645765789',
        'Hm_lvt_31dd95ba36e7f4183646dc46072a6e5d':'1645765789',
        'SESSION':'2e2f606b-07a3-4e7e-abaf-e91f947fdacc',
        '_hb_pgid':'356510',
        'Hm_lpvt_f737b389ea57a0a21e1ff802f849fbf0':'1645766424',
        'Hm_lpvt_31dd95ba36e7f4183646dc46072a6e5d':'1645766424',
        '_hb_ref_pgid':'356510',
        '_ga':'GA1.2.1020719568.1645766424',
        '_gid':'GA1.2.1032049669.1645766424',
        '_gat':'1'
    }
    headers = {
        'Host': 'simu.howbuy.com',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode':' navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://wallstreetcn.com/news/shares',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls, headers=self.headers, cookies=self.cookies, callback=self.parse_articleList)

    def parse_articleList(self,response):
        articleinfo_lis = response.xpath('//div[@class="newslist"]/ul/li[not(@class)]')
        url_list = []
        for article in articleinfo_lis:
            publish_time = article.xpath('./span[@class="listdata"]/text()').extract_first()
            url = article.xpath('./a/@href').extract_first()
            title = article.xpath('./a/text()').extract_first()
            if('|好买私募日报' in title):
                continue
            if (Contraler_Time.getCurDate('%Y-%m-%d') in publish_time):
                url_list.append((title, url))

        for url in url_list:
            if(Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="content"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first().replace(' ', '').replace('\n', '').replace('\t','')
            if (
                '免责声明' in paragraph or 0<int(len(paragraph))<=6 or '导言：' in paragraph or '风险提示：' in paragraph or '以供投资者参考' in paragraph
            ):
                continue
            if (paragraph):
                c = cleaner_paragraph.integratedOp(paragraph)
                if (int(len(c)) < 3):
                    pass
                else:
                    content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'' + imgsrc + '\'/>'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem





