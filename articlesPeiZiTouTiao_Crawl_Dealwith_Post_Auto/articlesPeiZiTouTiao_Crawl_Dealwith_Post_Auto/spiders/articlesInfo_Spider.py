"""
    这里爬取的是文章信息的列表
"""
import scrapy
from fake_useragent import UserAgent
from ..items import ArticlesInfoItem

class gppzSpider(scrapy.Spider):
    name = "ArticlesInfoSpider"
    allow_domains = "www.peizitoutiao.com"
    # 对应栏目名
    topicName = 'pzgs'  # 爬取的对应栏目名 改动的位置
    tableName = "tb_" + topicName +"_articleinfo"   # 对应数据库表明
    start_urls = "https://www.peizitoutiao.com/" + topicName + "/list-1-"

    def start_requests(self):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': str(UserAgent().random),
        }
        # gppz有23页，循环23次
        # gzpt有8页，循环8次
        for i in range(1, 9):
            url_ = self.start_urls + str(i) +".html"
            yield scrapy.Request(url=url_, callback=self.parse_articleInfo, headers=headers)
        # url_ = self.start_urls + str(1) +".html"
        # yield scrapy.Request(url=url_, callback=self.parse_articleInfo, headers=headers)

    # 获取文章信息列表
    def parse_articleInfo(self, response, **kwargs):
        articleList = response.xpath("//div[@class='gppzpt_fc']/ul//li")
        for article in articleList:
            articleInfoItem = ArticlesInfoItem()
            articleInfoItem['title'] = article.xpath(".//h2/text()").extract_first()
            articleInfoItem['author'] = "".join(article.xpath(".//div[@class='gppzpt_zx_author']/text()").extract()).replace(" ","").replace("\n","")
            articleInfoItem['publishTime'] = article.xpath(".//div[@class='gppzpt_zx_author']/span/text()").extract_first()
            articleInfoItem['url'] = self.allow_domains + '/' + article.xpath(".//div[@class='gppzpt_zx_title pull-right']//a/@href").extract_first()
            articleInfoItem['tag'] = article.xpath(".//div[@class='gppzpt_zx_tag']/a/text()").extract_first()
            articleInfoItem['tableName'] = self.tableName
            yield articleInfoItem
