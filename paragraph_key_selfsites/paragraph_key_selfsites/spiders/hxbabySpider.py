import scrapy
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
class HxbabySpider(scrapy.Spider):
    name = 'hxbabySpider'
    start_urls = [
        'https://www.hxbaby.com.cn/',
        'https://www.hxbaby.com.cn/zhpzptai/',
        'https://www.hxbaby.com.cn/sppzgs/',
        'https://www.hxbaby.com.cn/zxggpz/',
        'https://www.hxbaby.com.cn/sdpzpt/',
        'https://www.hxbaby.com.cn/pzptkh/'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response, **kwargs):
        # 本页的文章信息列表
        articleList = response.xpath("//div[@class='chapter-num chapter-show']/ul/li")
        articles_url_lis = []
        today_date = Contraler_Time.getCurDate('%m%d')
        for article in articleList:
            url_part = article.xpath(".//h2/a/@href").extract_first()
            article_url = 'https://www.hxbaby.com.cn' + url_part
            try:
                tag_ori = article.xpath(".//div[@class='clearfix address']/a[@class='biao qian label']/text()").extract_first()
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

