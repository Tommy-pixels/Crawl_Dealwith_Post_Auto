import scrapy,time
from fake_useragent import UserAgent
from ..tools import basic


def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class SougouWechatSpider(scrapy.Spider):
    name = 'sougouWechatSpider'
    start_url = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=%E8%82%A1%E7%A5%A8%E5%85%A5%E9%97%A8%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86&ie=utf8&_sug_=y&_sug_type_=&w=01019900&sut=1323&sst0=1637824112380&lkt=0%2C0%2C0'
    headers = {
        'Host': 'weixin.sogou.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://weixin.sogou.com/weixin?query=%E8%82%A1%E7%A5%A8%E5%85%A5%E9%97%A8%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86&_sug_type_=&sut=1323&lkt=0%2C0%2C0&s_from=input&_sug_=y&type=2&sst0=1637824112380&page=1&ie=utf8&w=01019900&dr=1',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    # ------------------------- 自动获取cookies和signature的方式
    sougou = basic.ConSelenium()
    res = sougou.open()
    sougou.browser.get(start_url)
    cookies = sougou.browser.get_cookies()
    sougou.browser.close()

    def start_requests(self):
        yield scrapy.Request(url=self.start_url, cookies=self.cookies, headers=self.headers, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        articleList = response.xpath("//ul[@class='news-list']//li")
        urlList = []

        for article in articleList:
            publishTime = article.xpath(".//span[@class='s2']//text()").extract_first().split("'")[1]
            url = 'https://weixin.sougou.com' + article.xpath(".//h3//a//@href").extract_first()
            urlList.append(url)
            # if(int(publishTime)>int(getSecondByDate(getCurDate()+' 00:00:00'))):
            #     urlList.append(url)
            # else:
            #     continue
        for url in urlList:
            print(self.cookies)
            print(url)
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        print("safs")
        print(response.text)
        print()


