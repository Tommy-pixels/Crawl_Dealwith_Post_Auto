import scrapy, time, json
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier

# 获取当前日期
def getCurDate(format='%Y%m%d'):
    return time.strftime(format, time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class ZhitongSpider(scrapy.Spider):
    name = 'zhitongSpider'
    start_url = 'https://www.zhitongcaijing.com/content/recommend.html?data_type=1&token=a87bcdaf54ff9fb5adca6538ee95eb191cf3588a&page={}'
    headers = {
        'Host': 'www.zhitongcaijing.com',
        'Connection': 'close',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'empty',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.zhitongcaijing.com/content/recommend.html',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'UM_distinctid=17f1a36bd0dde7-0fdbbb20cf0ca6-6373264-1fa400-17f1a36bd0edd8':'zh_choose_ztcj=jian',
        'Hm_lvt_798bcc2e164540abf265d2beeb49b3b0':'1645412280;',
        'PHPSESSID':'o6fh125740ga9fehqb1gp128fj;',
        'CNZZDATA1258425140':'1112334018-1645409919-%7C1645420725;',
        'Hm_lpvt_798bcc2e164540abf265d2beeb49b3b0':'1645421885'
    }

    def start_requests(self):
        for i in range(1,10):
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        li_lis = json.loads(response.text)['data']
        urlList = []
        for li in li_lis:
            publishTime = int(li['original_time'])
            if(publishTime<int(getSecondByDate(getCurDate() + ' 00:00:00'))):
                continue
            title = li['title']
            url = 'https://www.zhitongcaijing.com' + li['url']
            if (Base_Identifier.is_intterrogative(title) and url not in urlList):
                urlList.append(url)
        for url in urlList:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
        pList = response.xpath('//div[@class="news-body-content"]/p')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '')
            if (c != '' and '股市有风险' not in c and '作者：' not in c and '本文编选自' not in c and '风险提示：' not in c and '本文来源于' not in c and '编辑：' not in c ):
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem

