import time
import scrapy
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from .. import items
import json
from fake_useragent import UserAgent

def get_params():
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    browser = webdriver.Chrome(r"E:\Projects\webDriver\\chrome\\chromedriver.exe", options=option)
    start_urls = "https://www.gelonghui.com/"
    browser.get(start_urls)
    time.sleep(1)
    # 获取cookie
    dictCookies = browser.get_cookies()
    cookies = {}
    for item in dictCookies:
        key = item['name']
        cookies[str(key)] = str(item['value'])
    browser.close()
    # 获取version
    html = urlopen('https://www.gelonghui.com/hotpost').read()
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.select('script')
    # versionScript = browser.find_element_by_xpath("//script[not(@type or @charset or @src)]").text
    # version = str(versionScript).split("version:")[-1].split(",")[0].replace('"', "").strip()     # 读取不了script 为空
    version = scripts[0].contents[0].split("version:")[-1].split(",")[0].replace('"',"").strip()
    return {
        'cookies': cookies,
        'version': version
    }

class GelonghuiSpider(scrapy.Spider):
    name = 'gelonghuiSpider'
    start_url = 'https://www.gelonghui.com/api/topContent/list?page={}&size=20&version={}'
    headerStr = '''
        Host: www.gelonghui.com
        Connection: keep-alive
        sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
        Accept: application/json, text/plain, */*
        platform: web
        sec-ch-ua-mobile: ?0
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
        shortVersion: 9.8.1
        Client-Lang: zh-cn
        Sec-Fetch-Site: same-origin
        Sec-Fetch-Mode: cors
        Sec-Fetch-Dest: empty
        Referer: https://www.gelonghui.com/hotpost
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9
    '''
    # cookieStr = 'g_traceId=3ee91b33-a466-4bd3-ada5-8c733b626c0d; g_conversationId=03f2c; Hm_lvt_99cf2fc901f78474af7cf7a5b565deac=1635384215,1635386966; Hm_lpvt_99cf2fc901f78474af7cf7a5b565deac=1635387614'

    params = get_params()
    cookie = params['cookies']
    version = params['version']

    page = 1    # 一天（7之前）

    def start_requests(self):
        headerList = self.headerStr.split('\n')
        self.header = {}
        for headerItem in headerList:
            i = headerItem.strip().split(":")
            if (i != ['']):
                k = i[0]
                v = i[1]
                self.header[k] = v
        # cookieList = self.cookieStr.split(";")
        # self.cookie = {}
        # for cookieItem in cookieList:
        #     i = cookieItem.strip().split("=")
        #     k = i[0]
        #     v = i[1]
        #     self.cookie[k] = v
        self.start_url.format(str(self.page), self.version)
        yield scrapy.Request(self.start_url.format(self.page, self.version), callback=self.parse_list, headers=self.header, cookies=self.cookie)

    def parse_list(self, response):
        data = json.loads(response.text)
        cur_page = data['result']['page']
        articleInfoList = data['result']['contents']
        commentItem = items.CommentItem()
        for articleInfo in articleInfoList:
            articleData = articleInfo['data']
            commentNum = articleData['dynamicCount']['commentCount']
            commentList = articleData['comments']
            if(not commentList):
                continue
            if(len(commentList) >= commentNum):
                # 接口获取到的评论数据数量等于真实评论数量
                # 不需要进入对应页面爬取评论
                for commentInfo in commentList:
                    comment = commentInfo['content']
                    publishTime = commentInfo['createTimestamp']    # 评论发布时间
                    commentItem['comment'] = comment
                    commentItem['publishTime'] = publishTime
                    yield commentItem
            else:
                # 接口获取到的评论数量小于真实评论数量
                # 需要进入对应页面爬取评论
                articleUrl = articleData['route']
                id = articleData['id']
                commentApiUrl = 'https://www.gelonghui.com/api/comments/dynamic/{}/v2'.format(id)
                self.header['User-Agent'] = UserAgent().random
                yield scrapy.Request(commentApiUrl, callback=self.parse_commentApi, cookies=self.cookie, headers=self.header)
            publishTime = articleData['createTimestamp']    # 当前文章发布时间
        while(self.page <= 10):
            self.page = self.page + 1
            self.start_url.format(str(self.page), self.version)
            time.sleep(2)
            yield scrapy.Request(self.start_url.format(self.page, self.version), callback=self.parse_list, headers=self.header,cookies=self.cookie)

    def parse_commentApi(self, response):
        commentList = json.loads(response.text)['result']
        commentItem = items.CommentItem()
        if(commentList):
            for comment_ in commentList:
                comment = comment_['content']
                publishTime = comment_['createTimestamp']
                commentItem['comment'] = comment
                commentItem['publishTime'] = publishTime
                yield commentItem

