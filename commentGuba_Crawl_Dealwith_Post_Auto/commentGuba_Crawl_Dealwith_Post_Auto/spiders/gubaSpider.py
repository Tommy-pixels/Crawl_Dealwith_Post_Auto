import scrapy, time, json
from selenium import webdriver
from fake_useragent import UserAgent
from .. import items

def getCurYear():
    now = time.strftime("%Y-%m-%d", time.localtime())
    year = now.split('-')[0]
    return year

# 获取当前日期
def getCurDate():
    return time.strftime("%Y%m%d", time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date, formatStr='%Y%m%d %H:%M:%S'):
    b = time.strptime(date, formatStr)
    return time.mktime(b)


def translate_Headers_Row2Obj(headersRow):
    headerList = headersRow.split('\n')
    headers = {}
    for headerItem in headerList:
        i = headerItem.strip().split(":")
        if (i != ['']):
            k = i[0]
            v = i[1]
            headers[k] = v
    return headers

# 通过selenium获取指定信息的类
class GetParams_Selenium:
    def __init__(self, driverPath=r"E:\Projects\webDriver\\chrome\\chromedriver.exe"):
        option = webdriver.ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('useAutomationExtension', False)
        self.browser = webdriver.Chrome(driverPath, options=option)

    @classmethod
    def getCookies(self, url, browser=None):
        '''
        类方法，以对象形式输出指定链接返回的cookies
        :param url: 待打开的链接
        :param browser: 浏览器引擎
        :return: cookies对象
        '''
        browser.get(url)
        time.sleep(1)
        # 获取cookie
        dictCookies = browser.get_cookies()
        cookies = {}
        for item in dictCookies:
            key = item['name']
            cookies[str(key)] = str(item['value'])
        return cookies

    def getHeaders(self, url, browser):
        pass

    def get_params(self, url):
        cookies = self.getCookies(url, self.browser)
        headers = {}
        return {
            'cookies': cookies
        }


class GubaSpider(scrapy.Spider):
    name = 'gubaSpider'
    articleList_url = 'http://guba.eastmoney.com/default,99_{}.html'
    articleList_page = 7
    getDataListApi = 'http://guba.eastmoney.com/interface/GetData.aspx'
    param_path_commentList = 'reply/api/Reply/ArticleNewReplyList'
    param_path_commentReplyList = 'reply/api/Reply/ArticleReplyDetail'
    headersRom = '''
        Host: guba.eastmoney.com
        Connection: keep-alive
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Referer: http://guba.eastmoney.com/default,0_1.html
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9
    '''

    # 获取帖子列表html页面
    def start_requests(self):
        getparamsInstance = GetParams_Selenium()
        self.cookies = getparamsInstance.get_params(url='http://guba.eastmoney.com')['cookies']
        for i in range(8,12):
            self.headers = translate_Headers_Row2Obj(self.headersRom)
            self.headers['User-Agent'] = str(UserAgent().random)
            if(i%2 == 0):
                self.cookies = getparamsInstance.get_params(url='http://guba.eastmoney.com')['cookies']
            yield scrapy.Request(url=self.articleList_url.format(str(i)), callback=self.parse_articleList, cookies=self.cookies, headers=self.headers)
            time.sleep(2)

    # 获取帖子id 拼接成获取对应帖子评论的请求
    def parse_articleList(self, response):
        articleList = response.xpath("//div[@class='balist']//ul[@class='newlist']//li")
        articleIdList = []  # 文章id列表
        checkTime = int(getSecondByDate(getCurDate() + ' 00:00:00')) - 86400
        # 获取当前年份
        curYear = getCurYear()
        for articleSelector in articleList:
            commentNum = articleSelector.xpath(".//cite")[1].xpath(".//text()").extract_first().strip()
            articleUrl = articleSelector.xpath(".//span//a[@title]/@href").extract_first()
            print(articleUrl)
            refer = ','.join(articleUrl.split(',')[-2:])
            articleId = articleUrl.split(',')[-1].split('.')[0]

            if('/' in articleId):
                print(articleId)
                continue
            articleUpdateTime = curYear + articleSelector.xpath(".//cite")[4].xpath(".//text()").extract_first().strip().replace('-','') + ':00'

            if(int(commentNum)>0 and int(getSecondByDate(articleUpdateTime)) > checkTime and articleId not in articleIdList):
                articleIdList.append((refer,articleId))
        print(articleIdList)

        for refer, articleId in articleIdList:
            self.headers['User-Agent'] = str(UserAgent().random)
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            self.headers['Referer'] = 'http://guba.eastmoney.com/news,' + refer
            body = 'param=postid={}&sort=1&sorttype=1&p=1&ps=30' + '&path=reply/api/Reply/ArticleNewReplyList' + '&env=2'
            params = {}
            params['articleId'] = articleId
            params['curCommentPage'] = 1
            params['refer'] = refer
            yield scrapy.Request(url=self.getDataListApi, callback=self.parse_commentList, cookies=self.cookies, headers=self.headers, method='POST', body=body.format(str(articleId)), cb_kwargs=params)

    # 评论只有一页的处理
    def parse_commentList(self, response, articleId, curCommentPage, refer):
        commentObj = json.loads(response.text)
        commentCount = commentObj['count']
        # 把当前页面的评论内容处理了
        commentList = commentObj['re']
        commentIdList_hasReply = []
        commentItem = items.CommentItem()
        for commentInfo in commentList:
            comment = commentInfo['reply_text']
            publishTime = commentInfo['reply_publish_time']
            comment_id = commentInfo['reply_id']
            reply_count = commentInfo['reply_count']
            if(int(reply_count)>0 and comment_id not in commentIdList_hasReply):
                # 说明评论有回复内容，需要获取评论的回复数据
                commentIdList_hasReply.append((articleId,comment_id))
            # 最后判断发布时间
            checkTime = int(getSecondByDate(getCurDate() + ' 00:00:00'))-86400
            if(int(getSecondByDate(publishTime, formatStr='%Y-%m-%d %H:%M:%S'))<checkTime):
                # 不符合时间要求，不是24h内发表的评论
                continue

            # 過濾
            if ('#' in comment or '$' in comment or '@' in comment or '●' in comment or '发表于' in comment):
                continue

            # 清洗
            if ('&quot;' in comment):
                comment = comment.replace('&quot;', ' ')

            commentItem['comment'] = comment
            commentItem['publishTime'] = int(getSecondByDate(publishTime, formatStr='%Y-%m-%d %H:%M:%S'))
            yield commentItem

        # 针对有其它页码的评论
        if(int(commentCount)>30):
            # 判断是否是第一页，是的话才有如下获取其它页码数据的请求
            if(curCommentPage==1):
                # 评论有多页
                pageNum = int(commentCount/30)+1
                for i in range(2,pageNum):
                    body = 'param=postid={}&sort=1&sorttype=1&p={}&ps=30' + '&path=reply/api/Reply/ArticleNewReplyList' + '&env=2'.format(articleId,str(i))
                    params = {}
                    params['articleId'] = articleId
                    params['curCommentPage'] = i
                    params['refer'] = refer
                    yield scrapy.Request(url=self.getDataListApi, callback=self.parse_commentList, cookies=self.cookies,headers=self.headers, body=body, cb_kwargs=params)

        # 针对有回复消息的评论
        for articleId, commentId in commentIdList_hasReply:
            self.headers['User-Agent'] = str(UserAgent().random)
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            self.headers['Referer'] = 'http://guba.eastmoney.com/news,' + refer
            body = 'postid={}&replyid={}&sort=1&sorttype=1&ps=10&p=1' + '&path=reply/api/Reply/ArticleNewReplyList' + '&env=2'.format(articleId, commentId)
            yield scrapy.Request(url=self.getDataListApi, callback=self.parse_commentReplyList, cookies=self.cookies, headers=self.headers, body=body)

    # 评论的回复数据处理
    def parse_commentReplyList(self, response):
        replyObj = json.loads(response.text)
        commentItem = items.CommentItem()
        if(replyObj['re']):
            child_replys = replyObj['re']['child_replys']
            if(child_replys):
                for childReplyInfo in child_replys:
                    comment = childReplyInfo['reply_text']
                    publishTime = childReplyInfo['reply_publish_time']
                    # 最后判断发布时间
                    checkTime = int(getSecondByDate(getCurDate() + ' 00:00:00')) - 86400
                    if (int(getSecondByDate(publishTime)) < checkTime):
                        # 不符合时间要求，不是24h内发表的评论
                        continue

                    # 過濾
                    if ('#' in comment or '$' in comment or '@' in comment or '●' in comment or '发表于' in comment):
                        continue
                    # 清洗
                    if ('&quot;' in comment):
                        comment = comment.replace('&quot;', ' ')

                    commentItem['comment'] = comment
                    commentItem['publishTime'] = int(getSecondByDate(publishTime))
                    yield commentItem

