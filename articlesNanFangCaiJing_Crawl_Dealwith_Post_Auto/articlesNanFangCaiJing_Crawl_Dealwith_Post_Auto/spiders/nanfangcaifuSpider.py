import scrapy, random, time
from .. import items
from fake_useragent import UserAgent
class NanfangcaifuspiderSpider(scrapy.Spider):
    name = 'nanfangcaifuSpider'
    allowed_domains = 'www.southmoney.com'
    start_urls = ['http://www.southmoney.com/zhishi/gprm/']

    def randomSleep(self):
        sleepTime = random.randint(0, 5)
        time.sleep(sleepTime)
        pass

    def start_requests(self):
        for urlItem in self.start_urls:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random),
            }
            yield scrapy.Request(url=urlItem, callback=self.parse_ArticleInfo, headers=headers)

    def parse_ArticleInfo(self, response):
        kind = response.xpath("//div[@class='h2']/text()")[0].extract()  # 类别
        articleList = response.xpath("//ul[@class='newslist']//li")     # 文章链接
        articleInfoItem = items.articleInfoItem()
        urlList = []
        for article in articleList:
            url = "http://" + self.allowed_domains + article.xpath("./a/@href").extract_first()
            articleInfoItem["url"] = url
            articleInfoItem["title"] = article.xpath("./a/text()").extract_first()
            articleInfoItem["publishTime"] = article.xpath("./span[@class='date']/text()").extract_first()
            articleInfoItem['kind'] = kind
            urlList.append(url)
            yield articleInfoItem

        for articleUrl in urlList:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random),
            }
            yield scrapy.Request(url=articleUrl, callback=self.parse_ArticleContent, dont_filter=True)

    def parse_ArticleContent(self, response):
        paragraphList = response.xpath("//div[@class='articleCon']//p").xpath("string(.)").extract()
        articleContentItem = items.articleContentItem()
        for paragraph in paragraphList:
            articleContentItem['url'] = response.url
            articleContentItem['paragraph'] = paragraph
            yield articleContentItem
    def close(spider, reason):
        print("爬虫结束")