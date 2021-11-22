import scrapy, random, time
from .. import items
from fake_useragent import UserAgent
class NanfangcaifuspiderSpider(scrapy.Spider):
    name = 'nanfangcaifuInfoSpider'
    allowed_domains = 'www.southmoney.com'
    start_urls = ['http://www.southmoney.com/zhishi/gprm/', 'http://www.southmoney.com/zhishi/jsfx/', 'http://www.southmoney.com/zhishi/jbmfx/',
                  'http://www.southmoney.com/zhishi/chaogurumen/', 'http://www.southmoney.com/zhishi/Kxiantu/', 'http://www.southmoney.com/zhishi/Kxiantu/',
                  'http://www.southmoney.com/zhishi/gupiaomingci/', 'http://www.southmoney.com/zhishi/duanxian/', 'http://www.southmoney.com/zhishi/maimaidian/',
                  'http://www.southmoney.com/zhishi/xingu/', 'http://www.southmoney.com/zhishi/cybzs/', 'http://www.southmoney.com/zhishi/ruhexuangu/',
                  'http://www.southmoney.com/zhishi/ruhekanpan/', 'http://www.southmoney.com/zhishi/ruhejietao/', 'http://www.southmoney.com/zhishi/boduan/',
                  'http://www.southmoney.com/zhishi/fenshitu/', 'http://www.southmoney.com/zhishi/junxian/', 'http://www.southmoney.com/zhishi/chengjiaoliang/',
                  'http://www.southmoney.com/zhishi/dibufenxi/', 'http://www.southmoney.com/zhishi/dingbufenxi/', 'http://www.southmoney.com/zhishi/xipanbianpan/',
                  'http://www.southmoney.com/zhishi/chaodi/', 'http://www.southmoney.com/zhishi/gupiaogongshi/', 'http://www.southmoney.com/zhishi/kanpan/',
                  'http://www.southmoney.com/zhishi/jiangen/', 'http://www.southmoney.com/zhishi/zhangting/']

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
            yield scrapy.Request(url=urlItem, callback=self.parse_ArticleList, headers=headers)

    def parse_ArticleList(self, response):
        kind = response.xpath("//div[@class='h2']/text()")[0].extract()  # 类别
        articleList = response.xpath("//ul[@class='newslist']//li")     # 文章链接
        # for article in articleList:
        #     articleInfoItem = items.articleInfoItem()
        #     articleInfoItem["articleUrl"] = "http://" + self.allowed_domains + article.xpath("./a/@href").extract_first()
        #     articleInfoItem["articleTitle"] = article.xpath("./a/text()").extract_first()
        #     articleInfoItem["articlePublishTime"] = article.xpath("./span[@class='date']/text()").extract_first()
        #     articleInfoItem['kind'] = kind
        #     yield articleInfoItem

        for article in articleList:
            headers = {
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': str(UserAgent().random),
            }
            print("zai")
            yield scrapy.Request(url="http://"+self.allowed_domains + article.xpath("./a/@href").extract_first(), callback=self.parse_ArticleContent)

    def parse_ArticleContent(self, response):
        paragraphList = response.xpath("//div[@class='articleCon']//p/text()").extract()
        print("在parse_ArticleContent")
        for paragraph in paragraphList:
            articleContentItem = items.articleContentItem()
            articleContentItem['url'] = response.url
            articleContentItem['paragraph'] = paragraph
            yield articleContentItem
