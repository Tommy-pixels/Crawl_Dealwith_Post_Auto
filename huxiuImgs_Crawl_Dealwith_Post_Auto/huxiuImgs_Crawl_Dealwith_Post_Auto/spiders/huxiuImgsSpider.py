"""
    爬取虎嗅网-财经目录下所有文章的图片
    获取文章json数据的接口 为post请求 需要发送表单验证
    发送的表单如下：
        platform    www
        last_time   1628813160
        channel_id  115
"""
import scrapy, json, random
from .. import items
from fake_useragent import UserAgent
import time


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
    start_urls = "https://article-api.huxiu.com/web/channel/articleList"
    allowed_domains = ['huxiu.com']
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent':  str(UserAgent().random),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.huxiu.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.huxiu.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    # 要存放到的对应的数据库表名 注意这里要修改的 ------------------------------------------
    databaseTbName = 'tb_test'
    # 栏目Id  注意这里要修改的 ------------------------------------------
    channelId = 115 # 115是财经
    curTime = int(round(time.time()))    # 获取当前时间戳
    cookies = {
        'huxiu_analyzer_wcy_id':'4etqqzywwkxrfgrkd6v',
        'Hm_lvt_502e601588875750790bbe57346e972b':'1632276403',
        'Hm_lpvt_502e601588875750790bbe57346e972b':'1632277091',
        'hx_object_visit_referer_11_' + str(channelId):'https%3A%2F%2Fwww.huxiu.com%2F',
        # 'SERVERID':'3e2292d3f2b396659e73250c9fef164b|' + str(curTime) + '|1629852277'
    }

    def start_requests(self):
        # 注意这里要修改的 ------------------------------------------
        formdata = {
            'platform': 'www',
            'last_time' : str(int(getSecondByDate(getCurDate() + " 00:00:00"))), # 当前日期时间戳
            'channel_id' : str(self.channelId)
        }
        yield scrapy.FormRequest(self.start_urls, callback=self.parse, formdata=formdata, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        if(response.status==200):
            data = json.loads(response.body)["data"]
            dataList = data['datalist']
            articleInfo = items.articleInfoItem()
            # 在parse中返回的Item对象会传到Pipeline 返回的Request会加入请求队列
            for article in dataList:
                articleInfo['dateline'] = article['dateline']
                articleInfo['formatDate'] = article['formatDate']
                articleInfo['origin_pic_path'] = article['origin_pic_path']
                articleInfo['pic_path'] = article['pic_path']
                articleInfo['title'] = article['title']
                articleInfo['user_name'] = article['user_info']['username']
                articleInfo['user_uid'] = article['user_info']['uid']
                articleInfo['user_avatar'] = article['user_info']['avatar']
                articleInfo['databaseTbName'] = self.databaseTbName
                yield articleInfo
            theLastDateline = dataList[-1]['dateline']  # 用于获取新的文章列表数据
            # 更新一下cookie header 和 formdata
            formdata = {
                'platform': 'www',
                'last_time': str(theLastDateline),
                'channel_id': str(self.channelId)
            }
            self.headers = {
                'Connection': 'keep-alive',
                'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent':  str(UserAgent().random),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.huxiu.com',
                'Sec-Fetch-Site': 'same-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://www.huxiu.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            }
            curTime = int(round(time.time()))  # 获取当前时间戳

            # 条件判断主动令爬虫失效
            if (int(theLastDateline) <= int(curTime) - 17800):
                self.crawler.engine.close_spider(self, "失效 关闭爬虫")

            cookies = {
                'huxiu_analyzer_wcy_id': '5wwrfvzxus44v5ozeuf5',
                'Hm_lvt_502e601588875750790bbe57346e972b': '1629765918,1629852279',
                'Hm_lpvt_502e601588875750790bbe57346e972b': '1629852754',
                'hx_object_visit_referer_11_' + str(self.channelId): 'https%3A%2F%2Fwww.huxiu.com%2F',
                'SERVERID': '3e2292d3f2b396659e73250c9fef164b|' + str(curTime) + '|1629852277'
            }
            yield scrapy.FormRequest(self.start_urls, callback=self.parse, formdata=formdata, headers=self.headers,
                                     cookies=self.cookies)
            randomSleep()
