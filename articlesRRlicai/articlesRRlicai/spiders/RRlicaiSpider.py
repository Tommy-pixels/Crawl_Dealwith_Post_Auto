import scrapy
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner

class RRlicaiSpider(scrapy.Spider):
    name = 'rrlicaiSpider'
    start_url = 'https://www.rrlicai.com/gupiao'


    headers = {
        'Host': 'www.rrlicai.com',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User':'?1',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.rrlicai.com/gupiao',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        yield scrapy.Request(url=self.start_url, headers=self.headers, callback=self.parse_articleInfo)

    def parse_articleInfo(self,response):
        articleList = response.xpath('//ul[@class="post-loop post-loop-default cols-0"]/li')
        url_lis = []
        for article in articleList:
            url = article.xpath('.//h2/a/@href').extract_first()
            title = article.xpath('.//h2/a/text()').extract_first().strip()
            publishTime = article.xpath(".//div[@class='item-meta']/span[@class='item-meta-li date']/text()").extract_first()
            if('分钟前' in publishTime or '小时前' in publishTime):
                url_lis.append((title, url))
        for url in url_lis:
            if(Base_Identifier.is_intterrogative(url[0])):
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url=url[1], headers=self.headers, callback=self.parse_content, cb_kwargs=add_param)

    def parse_content(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="entry-content clearfix"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first().replace(' ', '').replace('\n', '').replace('\t','').replace(' ','')
            if (
                    '本报记者' in paragraph or '注：' in paragraph or '原文标题' in paragraph or '仅供参考' in paragraph or '数据来源：' in paragraph
            ):
                continue
            if (paragraph):
                c = Base_Cleaner.del_content_between(c, s_left='（来源：', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）')
                if (c.startswith('，') or c.startswith(',')):
                    c = c[1:]
                c = cleaner_paragraph.integratedOp(c)
                if (int(len(c)) < 3):
                    pass
                else:
                    content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    if('lazy.png' in imgsrc):
                        continue
                    content = content + '<img src=\'' + imgsrc + '\'/>'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem

