import scrapy
from .. import items
from fake_useragent import UserAgent
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph

class CngoldSpider(scrapy.Spider):
    name = "cngoldSpider"
    allowed_domains = 'stock.cngold.org'
    start_url = ['https://stock.cngold.org/news/']

    def start_requests(self):
        for urlItem in self.start_url:
            header = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random)
            }
            yield scrapy.Request(url=urlItem, callback=self.parse_articleInfo, headers=header)

    def parse_articleInfo(self, response):
        articleList = response.xpath("//ul[@class='news_list']")[0].xpath("./li")
        # articleInfoItem = items.ArticleInfoItem()
        urlList = []
        for article in articleList:
            title = article.xpath("./a")[1].xpath('./text()').extract_first()
            url = article.xpath("./a")[1].xpath('./@href').extract_first()
            publishTime = article.xpath("./span[@class='fr']/text()").extract_first()
            if(publishTime.split(' ')[0] == Contraler_Time.getCurDate('%m-%d')):
                urlList.append((title, url))
        cb_p = {}
        for articleUrl in urlList:
            if(Base_Identifier.is_intterrogative(articleUrl[0])):
                cb_p['title'] = articleUrl[0]
                header = {
                    'Connection': 'keep-alive',
                    'Accept': 'application/json, text/plain, */*',
                    'User-Agent': str(UserAgent().random)
                }
                yield scrapy.Request(url=articleUrl[1], callback=self.parse_articleContent, headers=header, dont_filter=True, cb_kwargs=cb_p)


    def parse_articleContent(self, response, title):
        content = ''
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath("//div[@class='article_con']/p")
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = "".join(p.xpath('string(.)').extract())
            if (c != ''):
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）')
                if (c.startswith('，') or c.startswith(',')):
                    c = c[1:]
                c = cleaner_paragraph.integratedOp(c)
                content = content + "<p>" + c + "</p>"

            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'' + imgsrc + '\'/>'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem
