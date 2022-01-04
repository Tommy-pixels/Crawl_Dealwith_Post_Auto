import scrapy
from .. import items

class aigupiaoSpider(scrapy.Spider):
    name = 'aigupiaoSpider'
    start_url = 'https://www.aigupiao.com/news/igp_sina.php'
    headers = {
        'Host': 'www.aigupiao.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.aigupiao.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'PHPSESSID':'4b8c6a7f51674bd6db000fe7d9e1ec4a',
        'Hm_lvt_4c4d23fdfb3352f7bbb44af9c54f9bf1':'1639359971',
        'Hm_lpvt_4c4d23fdfb3352f7bbb44af9c54f9bf1':'1639364534'
    }
    def start_requests(self):
        yield scrapy.Request(url=self.start_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        articleList = response.xpath("//div[@class='listbox2']/div[@class='item']")
        urlList = []
        for article in articleList:
            publishTime = article.xpath(".//div[@class='foot1']//div[@class='time1']//text()").extract_first()
            if('日' in publishTime):
                continue
            url = 'https://www.aigupiao.com' + article.xpath(".//div[@class='title1']/a/@href").extract_first()
            if(url not in urlList):
                urlList.append(url)

        for url in urlList:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)


    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1/text()').extract_first()
        pList = response.xpath('//div[@class="newstextbox"]//div')[0].xpath(".//div[@class='init-photo-gallery news_content init-gallery']/*")
        content = ''
        for p in pList:
            c = p.xpath('string(.)').extract_first()
            if (c != '' and '爱股票社区' not in c and '作者个人' not in c and '仅供参考' not in c and '笔者简介' not in c and '转载' not in c and '文章来源：' not in c
                and '作者：' not in c and '来源：' not in c):
                content = content + '<p>' + p.xpath('string(.)').extract_first() + '</p>'
            if(p.xpath('.//img')!=[]):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'
        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


