import scrapy
from fake_useragent import UserAgent
from auto_datahandler.basement__ import ContralerTime
from .. import items

class XinhuaSpider(scrapy.Spider):
    name = 'xinhuaSpider'
    start_url = 'http://www.news.cn/money/index.html'

    headers = {
        'Host': 'www.news.cn',
        'Connection': 'close',
        'User-Agent': str(UserAgent().random),
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': 'http://www.news.cn/money/index.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {}

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        articleinfolis = response.xpath("//div[@class='list']/div[@id='content-list']/*")
        urlList = []
        for article in articleinfolis:
            publishTime = article.xpath(".//div[@class='time']//text()").extract_first()
            u_ = article.xpath(".//div[@class='tit']//a/@href").extract_first()
            if (u_ == None):
                continue
            if('www.news.cn' not in u_):
                    url = 'http://www.news.cn' + u_
            else:
                url = u_
            if("".join(publishTime.split('-')) == ContralerTime.Contraler_Time.getCurDate("%Y%m%d")):
                urlList.append(url)

        for url in urlList:
            yield scrapy.Request(url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        articleItem = items.ArticleItem()
        pList = response.xpath("//div[@id='detail']/*[@id='detailContent']").xpath('./*')
        content = ''
        title = response.xpath('//h1').xpath('string(.)').extract_first()
        for p in pList:
            c = p.xpath('string(.)').extract_first()
            if(c!=''):
                content =  content + '<p>' + c + '</p>'
            if(p.xpath('.//img')!=[]):
                for img in p.xpath('.//img'):
                    content = content + '<img src=\'' + img.xpath('.//@src').extract_first() + '\'/>'
        articleItem['content'] = content
        articleItem['title'] = title
        yield articleItem