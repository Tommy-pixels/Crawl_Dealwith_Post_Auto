import scrapy
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time

class anxinscSpider(scrapy.Spider):
    name = "anxinscSpider"
    start_urls = [
        'https://www.anxinsc.com/',
        'https://www.anxinsc.com/pzcg/',
        'https://www.anxinsc.com/pzpt/',
        'https://www.anxinsc.com/zxpz/',
        'https://www.anxinsc.com/pzfw/'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_Info)

    def parse_Info(self, response, **kwargs):
        # 获取文章列表
        articleList = response.xpath("//div[@class='article-list list-show']/ul/li")
        urlKind = response.url.split('/')[-2]
        articleUrlList = []
        today = Contraler_Time.getCurDate('%m%d')
        for article in articleList:
            title = article.xpath(".//h2/a").xpath("string(.)").extract_first()
            url_part = article.xpath(".//h2/a/@href").extract_first()
            url = response.url + url_part.replace('/' + urlKind + '/', "")
            tag_ori = article.xpath(".//div[@class='right-bottom']/span[@class='name']/text()").extract_first()
            publish_date = url_part.split('/')[-2]
            if(publish_date == today):
                articleUrlList.append((url, tag_ori))
        for urlItem in articleUrlList:
            add_para = {}
            add_para['tag_ori'] = urlItem[1]
            yield scrapy.Request(url=urlItem[0], callback=self.parse_content, cb_kwargs=add_para, dont_filter=True)


    def parse_content(self, response, tag_ori):
        # 对文章内容进行处理
        paragraphList = response.xpath("//div[@class='article-content']/p").xpath("string(.)").extract()
        contentItem = items.ArticleContentItem()
        for i in range(1, len(paragraphList) - 1):
            if (paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                contentItem['paragraph'] = paragraphList[i]
                contentItem['tag_ori'] = tag_ori
                yield contentItem
