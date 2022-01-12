import scrapy
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
class NbhxedudaSpider(scrapy.Spider):
    name = 'nbhxeduSpider'
    start_urls = [
        'https://www.nbhxedu.com/',
        'https://www.nbhxedu.com/tzpz/',
        'https://www.nbhxedu.com/pzcgpt/',
        'https://www.nbhxedu.com/wspz/',
        'https://www.nbhxedu.com/ggcg/',
        'https://www.nbhxedu.com/pzcx/'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response, **kwargs):
        # 本页的文章信息列表
        articleList = response.xpath("//div[@class='article-list list-show']/ul/li")
        articles_url_lis = []
        today_date = Contraler_Time.getCurDate('%m%d')
        for article in articleList:
            url_part = article.xpath(".//h2/a/@href").extract_first()
            article_url = 'https://www.nbhxedu.com' + url_part
            try:
                tag_ori = article.xpath(".//div[@class='right-bottom']/a[@class='biao qian label']/text()").extract_first()
            except Exception as e:
                continue
            if (not tag_ori):
                continue
            publish_date = url_part.split('/')[-2]
            if(today_date!=publish_date):
                continue
            else:
                articles_url_lis.append((article_url, tag_ori))
        for url in articles_url_lis:
            add_para = {}
            add_para['tag_ori'] = url[1]
            yield scrapy.Request(url=url[0], callback=self.parse_paragraph, dont_filter=True, cb_kwargs=add_para)

    def parse_paragraph(self, response, tag_ori):
        # 对文章内容进行处理
        paragraphList = response.xpath("//div[@class='article-content']/p").xpath("string(.)").extract()
        paragraphItem = items.ParagraphItem()
        for i in range(1, len(paragraphList) - 1):
            if(paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                paragraphItem['paragraph'] = paragraphList[i]
                paragraphItem['tag_ori'] = tag_ori
                yield paragraphItem

