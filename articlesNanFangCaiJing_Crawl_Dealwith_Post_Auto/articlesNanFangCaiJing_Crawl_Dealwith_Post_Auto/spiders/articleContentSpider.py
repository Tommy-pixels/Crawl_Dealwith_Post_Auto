
import scrapy, random, time, pymysql
from .. import items
from fake_useragent import UserAgent


def getUrlsList():
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="nanfangcaifudatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    sql = "select * from `nanfangcaifudatabase`.`tb_articlescontent`;"
    cursor.execute(sql)
    result = cursor.fetchall()
    urlList = []
    for item in result:
        urlList.append(item[1])
    return urlList


class NanfangcaifuspiderSpider(scrapy.Spider):
    name = 'nanfangcaifuContentSpider'
    allowed_domains = 'www.southmoney.com'
    # start_urls = getUrlsList()

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
            yield scrapy.Request(url=urlItem, callback=self.parse_ArticleContent, headers=headers)


    def parse_ArticleContent(self, response):
        paragraphList = response.xpath("//div[@class='articleCon']//p/text()").extract()
        for paragraph in paragraphList:
            articleContentItem = items.articleContentItem()
            articleContentItem['url'] = response.url
            articleContentItem['paragraph'] = paragraph.replace("'","’")
            yield articleContentItem
