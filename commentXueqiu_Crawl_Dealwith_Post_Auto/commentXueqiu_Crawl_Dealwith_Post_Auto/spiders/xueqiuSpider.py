import scrapy
from selenium import webdriver
from ..items import CommentItem
from ..items import ArticleInfoItem
import json, time

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d')
    return time.mktime(b)

def get_cookies():
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(executable_path="E:\Projects\webDriver\\chrome\\chromedriver.exe", options=option)
    start_urls = "https://xueqiu.com/today/"
    browser.get(start_urls)
    # 获取cookie
    dictCookies = browser.get_cookies()
    cookies = {}
    for item in dictCookies:
        key = item['name']
        cookies[str(key)] = str(item['value'])
    browser.close()
    return cookies

class xueqiuSpider(scrapy.Spider):
    name = 'xueqiuSpider'
    allowed_domain = 'xueqiu.com'
    start_urls = 'https://xueqiu.com/statuses/hot/listV2.json?since_id=-1&max_id=-1&size=15'
    comment_reply_api = 'https://xueqiu.com/comments/replies.json?id={}&page=1&count=20&type=0' # 评论回复的接口

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # cookieStr = "device_id=b3f9039fdd4d72371c3a0ba4809b128b; acw_tc=2760829816346259483943935e10cdfc96de0575479ba5b17ad26d5e34ef1a; s=bt12188nhm; xq_a_token=87397660f9d0893a50ec8461b8544612e877c6d5; xq_r_token=a5352df548f3835293a625883fdc15af94c6655e; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTYzNzE3MjM1OSwiY3RtIjoxNjM0NjI1OTU4Nzk2LCJjaWQiOiJkOWQwbjRBWnVwIn0.FraQPmLSR39cfYp39l9-ULCPhCfR3f7gB_KZ3DTtVJbdB3POJySVfKoOzRkjEft_afxpfXCBbYlbb4aXVLNvqDT9QwlnZ_7Q5C0jarokIrCaZLT2jP5NBUopPkXbtzINScqdsMv_xSrKZ5U29D0a6QLud7iKXbo_O_HZGGwbuZ9DF0IPKmtf_bpAadj8Q48EyKuL9e_lQAh1IxKYD-SWtzprR1PQsEZYeZkkUZbmnGguVfnwTaxBsjYgFtVtJl8jQNl92K1tiYftO4tg5Q-eBqMpi33_e5dKspJLE-d3DDPt6DU4XwB7LNpRtBa665hPCi-awhe-4sSnOz1LliTcgQ; u=601634625959062; Hm_lvt_1db88642e346389874251b5a1eded6e3=1634518707,1634525419,1634540466,1634625959; __utma=1.676855306.1634625959.1634625959.1634625959.1; __utmc=1; __utmz=1.1634625959.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=1.1.10.1634625959; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1634626649"
    cookies = get_cookies()
    count = 50  # 设置每次请求获取多少条数据 雪球网最多每次获取50条
    times = 0

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, cookies=self.cookies, headers=self.header, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        articleinfoItem = ArticleInfoItem()
        resJson = json.loads(response.body)
        next_max_id = resJson['next_max_id']
        dataList = resJson['items']
        articleUrlList = []

        for li in dataList:
            original_status = li['original_status']
            articleUrl = "https://xueqiu.com" + original_status['target']
            commentUrl = "https://xueqiu.com/statuses/comments.json?id=" + original_status['target'].split('/')[-1] + "&count=" + str(self.count) +"&page=1&reply=true&asc=false&type=status&split=true"
            publishTime = original_status['created_at'] # 发表的时间戳
            # 获取当前毫秒级时间戳
            curTimeSecond = int(time.time()) * 1000
            # 获取今天凌晨0点毫秒级时间戳
            yesterday = int(getSecondByDate(getCurDate())) * 1000
            if(publishTime>yesterday and publishTime<curTimeSecond and commentUrl not in articleUrlList):
                articleUrlList.append(commentUrl)
            articleinfoItem['url'] = commentUrl
            articleinfoItem['publishTime'] = publishTime
            yield articleinfoItem

        for url in articleUrlList:
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.header, callback=self.parse_comment)

        if(self.times<9):
            next_url = 'https://xueqiu.com/statuses/hot/listV2.json?since_id=-1&max_id=' + str(next_max_id) + '&size=15'
            self.times = self.times + 1
            yield scrapy.Request(url=next_url, cookies=self.cookies, headers=self.header, callback=self.parse_articleInfo)

    def parse_comment(self, response):
        resJson = json.loads(response.body)
        commentsList = resJson['comments']
        max_page = resJson['maxPage'] # 评论页数
        cur_page = resJson['page'] # 当前页码
        commentItem = CommentItem()
        comentReplyList = []
        if(int(max_page)!= 1 and int(cur_page)==1):
            # 评论有多页的时候
            urlId = response.url.split("&")[0].split("id=")[-1]
            for i in range(2, max_page+1):
                url = "https://xueqiu.com/statuses/comments.json?id=" + urlId + "&count=" + str(self.count) +"&page=" + str(i) + "&reply=true&asc=false&type=status&split=true"
                yield scrapy.Request(url=url, cookies=self.cookies, headers=self.header, callback=self.parse_comment)
        else:
            pass

        for commentli in commentsList:
            # 過濾
            if ('#雪球' in commentli['text'] or '#' in commentli['text'] or '雪球' in commentli['text']):
                continue
            commentItem['comment'] = commentli['text']
            commentItem['publishTime'] = commentli['created_at']
            commentItem['fromUrl'] = response.url
            # 评论的回复
            reply_count = commentli['reply_count']
            commentId = commentli['id']
            if(int(reply_count)>1 and self.comment_reply_api.format(commentId) not in comentReplyList):
                comentReplyList.append(self.comment_reply_api.format(commentId))
            yield commentItem
        for replyUrl in comentReplyList:
            yield scrapy.Request(url=replyUrl, cookies=self.cookies, headers=self.header, callback=self.parse_comment_reply)

    def parse_comment_reply(self,response):
        resJson = json.loads(response.body)
        repliesList = resJson['replies']
        commentItem = CommentItem()
        for reply in repliesList:
            if('#雪球' in reply['text'] or '#' in reply['text'] or '雪球' in reply['text']):
                continue
            commentItem['comment'] = reply['text']
            commentItem['publishTime'] = reply['created_at']
            commentItem['fromUrl'] = response.url
            yield commentItem