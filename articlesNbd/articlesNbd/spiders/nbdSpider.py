import scrapy, time
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner import cleaner_article


# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class NbdSpider(scrapy.Spider):
    name = 'nbdSpider'
    start_url = 'http://www.nbd.com.cn/columns/3'
    headers = {
        'Host': 'www.nbd.com.cn',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://www.nbd.com.cn/columns/3/page/3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'BAIDU_SSP_lcr':'https://www.baidu.com/link?url=S4S_TL9RLraqx3Z62mQIN6MEtAfcDxVugDAIzd9OVwS&wd=&eqid=afed98a1000683c10000000661c2c393',
        'Hm_lvt_de6470f7123b10c2a7885a20733e9cb1':'1640154008',
        '_nbd_session_id':'9aec8f18e56c0ec0545cfb306225996e',
        'Hm_lpvt_de6470f7123b10c2a7885a20733e9cb1':'1640154676'
    }

    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        yield scrapy.Request(url=self.start_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        mlist = response.xpath("//div[@class='m-list']")
        if(len(mlist)!=1):
            for i in mlist:
                channel_time = "".join(i.xpath('./p[@class="u-channeltime"]')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ', '').split("-"))
                if(channel_time==getCurDate()):
                    articleList = i.xpath('./ul/li')
                    break
        else:
            articleList = mlist.xpath('./ul/li')
        urlList = []
        for article in articleList:
            url_part = article.xpath(".//a/@href").extract_first()
            if('nbd_live' in url_part):
                continue
            url = 'http:' + url_part
            if (url not in urlList):
                urlList.append(url)

        for url in urlList:
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
        pList = response.xpath('//div[@class="g-articl-text"]/p')
        content = ''
        word_lis = [
            '公众号）', '微博）', '新闻）', '时报）', '日报）'
        ]
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
            if ('扫描下方二维码' in c or '每日经济新闻综合' in c or '未经许可禁止转载' in c or '原创文章｜' in c):
                break
            if('每日经济新闻综合' in c):
                continue
            for i in word_lis:
                if (i in c):
                    c = cleaner_article.Cleaner_Article().del_content_between(c, s_left='（', s_right=i)
            if (c != '' and '每经编辑：' not in c and '来源：' not in c and '仅供参考' not in c and '编辑：' not in c and '校对|' not in c and '编辑|' not in c
                    and '记者：' not in c and '声明：' not in c and '排版：' not in c and '视觉：' not in c and '封面：' not in c and '整理：' not in c
                    and '每经记者' not in c and ' 每经编辑' not in c and ' 每经评论员' not in c and '（北京日报）' not in c and '每经编辑' not in c and '记者|' not in c
            ):
                content = content + '<p>' + c + '</p>'

            if (p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem
