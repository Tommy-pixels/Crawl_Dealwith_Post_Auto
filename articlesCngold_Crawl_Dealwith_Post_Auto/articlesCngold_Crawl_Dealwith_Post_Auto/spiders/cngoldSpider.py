import scrapy
from .. import items
from fake_useragent import UserAgent
class CngoldSpider(scrapy.Spider):
    name = "cngoldSpider"
    allowed_domains = 'stock.cngold.org'
    start_url = ['https://stock.cngold.org/rumen/index.html']

    def start_requests(self):
        for urlItem in self.start_url:
            header = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random)
            }
            yield scrapy.Request(url=urlItem, callback=self.parse_articleInfo, headers=header)

    def parse_articleInfo(self, response):
        kind = response.xpath("//div/p[@class='ptit channel_list_tit']/text()")[0].extract().strip()
        articleList = response.xpath("//ul[@class='news_list']")[0].xpath("./li")
        articleInfoItem = items.ArticleInfoItem()
        urlList = []
        for article in articleList:
            url = article.xpath("./a/@href").extract_first()
            publishTime = article.xpath("./span[@class='fr']/text()").extract_first()
            articleInfoItem['url'] = url
            articleInfoItem['title'] = article.xpath('./a/text()').extract_first()
            articleInfoItem['publishTime'] = publishTime
            articleInfoItem['kind'] = kind
            if(publishTime.split('-')[0] == '2021'):
                urlList.append(url)
            yield articleInfoItem
        for articleUrl in urlList:
            header = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random)
            }
            yield scrapy.Request(url=articleUrl, callback=self.parse_articleContent, headers=header, dont_filter=True)


    def parse_articleContent(self, response):
        paragraphList = response.xpath("//div[@class='article_con']/p").xpath("string(.)").extract()
        articleContentItem = items.ArticleContentItem()
        for paragraph in paragraphList:
            articleContentItem['url'] = response.url
            articleContentItem['paragraph'] = paragraph
            yield articleContentItem

    def close(spider, reason):
        print("爬虫结束")