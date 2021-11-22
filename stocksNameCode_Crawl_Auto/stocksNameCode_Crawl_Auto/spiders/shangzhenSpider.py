import scrapy
from ..items import NameCodeItem
class stockSpider(scrapy.Spider):
    name = "StcockNameCodeSpider"
    allowed_domains = 'banban.cn'
    # 'https://www.banban.cn/gupiao/list_sz.html'
    # 'https://www.banban.cn/gupiao/list_cyb.html'
    # 'https://www.banban.cn/gupiao/list_sh.html'
    start_urls = [
        'http://www.ytwhw.com/gupiao/list_sh.html',
        'http://www.ytwhw.com/gupiao/list_sz.html',
        'http://www.ytwhw.com/gupiao/list_cyb.html',
        'http://www.ytwhw.com/gupiao/list_kcb.html'
    ]


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        belong = response.url.split('_')[1].split('.')[0]
        nameCodeList = response.xpath("//div[@class='u-postcontent cz']/div[@class='gnlist']/ul/li/a/text()").extract()
        namecodeItem = NameCodeItem()
        for item in nameCodeList:
            item = item.rstrip(')')
            li = item.split('(')
            namecodeItem['name'] = li[0]
            namecodeItem['code'] = li[1]
            namecodeItem['belong'] = belong
            yield namecodeItem
