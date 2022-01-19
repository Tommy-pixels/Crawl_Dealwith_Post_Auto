"""
    爬取虎嗅网-财经目录下所有文章的图片
    获取文章json数据的接口 为post请求 需要发送表单验证
    发送的表单如下：
        platform    www
        last_time   1628813160
        channel_id  115
"""
import scrapy, json, random,re
from .. import items
from fake_useragent import UserAgent
import time
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph


# --------------------------- 随机时间休眠 ----------------------------------
# 随机时间
def randomSleep():
    sleepTime = random.randint(0,2)
    time.sleep(sleepTime)
    pass

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class huxiuSpider(scrapy.Spider):
    name = "huxiuSpider"
    start_urls = "https://article-api.huxiu.com/web/article/articleList"
    allowed_domains = ['huxiu.com']
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': str(UserAgent().random),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.huxiu.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.huxiu.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    # 要存放到的对应的数据库表名 注意这里要修改的 ------------------------------------------
    databaseTbName = 'articledatabase'
    # 栏目Id  注意这里要修改的 ------------------------------------------
    curTime = int(round(time.time()))    # 获取当前时间戳
    cookies = {
        'huxiu_analyzer_wcy_id':'435y6rpau3gi2h5ex075b',
        'Hm_lvt_502e601588875750790bbe57346e972b':'1639374909',
        'Hm_lpvt_502e601588875750790bbe57346e972b':'1639375453',
    }

    def start_requests(self):
        # 注意这里要修改的 ------------------------------------------
        formdata = {
            'platform': 'www',
            'recommend_time' : str(int(getSecondByDate(getCurDate() + " 00:00:00"))), # 当前日期时间戳
            'pagesize' : str(22)
        }
        yield scrapy.FormRequest(self.start_urls, callback=self.parse_info, formdata=formdata, headers=self.headers, cookies=self.cookies)

    def parse_info(self, response, **kwargs):
        if(response.status==200):
            data = json.loads(response.body)["data"]
            dataList = data['dataList']
            # 在parse中返回的Item对象会传到Pipeline 返回的Request会加入请求队列
            urlList = []
            for article in dataList:
                url = 'https://www.huxiu.com/article/' + article['aid'] + '.html'
                publishTime = article['formatDate']
                if('小时前' in publishTime and url not in urlList):
                    headers = {
                        'Host': 'www.huxiu.com',
                        'Connection': 'keep-alive','Cache-Control': 'max-age=0',
                        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                        'sec-ch-ua-mobile': '?0',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': str(UserAgent().random),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-User': '?1',
                        'Sec-Fetch-Dest': 'document',
                        'Referer': 'https://www.huxiu.com/article/',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9'
                    }
                    yield scrapy.FormRequest(
                        url,
                        callback=self.parse_content,
                        headers=headers,
                        cookies=self.cookies
                    )
            theLastDateline = dataList[-1]['dateline']  # 用于获取新的文章列表数据
            # 更新一下cookie header 和 formdata
            formdata = {
                'platform': 'www',
                'recommend_time': str(theLastDateline),
                'pagesize': str(22)
            }
            curTime = int(round(time.time()))  # 获取当前时间戳
            # 条件判断主动令爬虫失效
            # if (int(theLastDateline) <= int(curTime) - 86400):
            #     self.crawler.engine.close_spider(self, "失效 关闭爬虫")
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.FormRequest(
                self.start_urls,
                callback=self.parse_info,
                formdata=formdata,
                headers=self.headers,
                cookies=self.cookies
            )
            randomSleep()

    def parse_content(self, response):
        title = response.xpath('//h1').xpath('string(.)').extract_first()
        content = ''
        pList = response.xpath('//div[@id="article-content"]/*')
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = p.xpath('string(.)').extract_first()
            if ('参考资料' in c or '参考链接' in c or '参考文献' in c):
                break
            if (c != '' and '本文来自' not in c and '参考链接' not in c and '参考资料' not in c
                    and '作者：' not in c and '（应受访者要求，文中均为化名）' not in c and '原文链接' not in c and '扫描图末二维码' not in c and '虎嗅注' not in c
                    and '作者 |' not in c and '头图 |' not in c and '出品 |' not in c and '设计 |' not in c  and '题图 |' not in c and '来源 |' not in c
                    and '作者｜' not in c and '头图｜' not in c and '出品｜' not in c and '设计｜' not in c  and '题图｜' not in c and '来源｜' not in c
                    and '本文不构成' not in c and '来源：' not in c
            ):
                if ('化名' in c):
                    if(re.compile(u"（.*?化名）").match(c)):
                        if (len(re.compile(u"（.*?化名）").match(c)[0]) <= 20):
                            c = re.sub(u"（.*?化名）", "", c)
                        else:
                            pass
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    content = content + '<img src="' + img.xpath('./@_src').extract_first() + '"/>'


        articleContentItem = items.ArticleContentItem()
        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


