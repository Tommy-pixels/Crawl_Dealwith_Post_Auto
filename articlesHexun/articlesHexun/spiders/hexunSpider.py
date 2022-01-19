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

class NbdSpider(scrapy.Spider):
    name = 'hexunSpider'
    start_url = 'http://news.hexun.com/domestic/'
    headers = {
        'Host': 'news.hexun.com',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://news.hexun.com/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'UM_distinctid':'17de4d857f3a1f-07ae011523a18b-6373264-1fa400-17de4d857f477c',
        'cn_1263247791_dplus':'%7B%22distinct_id%22%3A%20%2217de4d857f3a1f-07ae011523a18b-6373264-1fa400-17de4d857f477c%22%2C%22userFirstDate%22%3A%20%2220211223%22%2C%22userID%22%3A%20%220%22%2C%22userName%22%3A%20%22%22%2C%22userType%22%3A%20%22loginuser%22%2C%22userLoginDate%22%3A%20%2220211223%22%2C%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201640222781%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201640222781%2C%22initial_view_time%22%3A%20%221640219641%22%2C%22initial_referrer%22%3A%20%22http%3A%2F%2Fnews.hexun.com%2F%22%2C%22initial_referrer_domain%22%3A%20%22news.hexun.com%22%7D'
    }

    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        yield scrapy.Request(url=self.start_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        li_lis = response.xpath('//div[@class="mainboxcontent"]/div')[1].xpath('./li')
        urlList = []
        for article in li_lis:
            publishTime = article.xpath('./span/text()').extract_first().split(' ')[0].replace('/','').replace('(', '')
            if(publishTime!=getCurDate(format='%m%d')):
                continue
            url = article.xpath("./a/@href").extract_first()
            if (url not in urlList):
                urlList.append(url)
        for url in urlList:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
        pList = response.xpath('//div[@class="art_contextBox"]/p')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '')
            if ('扫描下方二维码' in c or '商报记者' in c):
                break
            if (c != '' and '中新经纬摄' not in c and '来源：' not in c and '仅供参考' not in c and '编辑：' not in c
                    and '记者：' not in c and '声明：' not in c and '排版：' not in c and '视觉：' not in c and '封面：' not in c and '整理：' not in c
                    and '打开APP 阅读最新报道' not in c and '转载请注明' not in c and '责任编辑' not in c and '作者：'not in c and '附表：' not in c and '（作者' not in c
            ):
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem
