import scrapy, time
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph

# 获取当前日期
def getCurDate(format='%Y%m%d'):
    return time.strftime(format, time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class DongjinrongSpider(scrapy.Spider):
    name = 'dongjinrongSpider'
    start_url = 'https://www.icttk.com/gupiao/page{}.html'
    headers = {
        'Host': 'www.icttk.com',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.icttk.com/gupiao/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'Hm_lvt_79c80a6d9d31213f06a0b48cd7d060f4':'1644801515',
        'Hm_lpvt_79c80a6d9d31213f06a0b48cd7d060f4':'1644802483'
    }

    def start_requests(self):
        for i in range(1,10):
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        li_lis = response.xpath('//div[@class="blogs"]/ul/li')
        urlList = []
        for li in li_lis:
            _publishTime = li.xpath('.//span[@class="blogs_time"]/text()').extract_first()
            publishTime = _publishTime.split('-')[1] + _publishTime.split('-')[2]
            if(publishTime!=getCurDate(format='%m%d')):
                continue
            url = li.xpath("./a/@href").extract_first()
            if (url not in urlList):
                urlList.append(url)
        for url in urlList:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
        pList = response.xpath('//div[@class="content"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '')
            if (c != ''):
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem

