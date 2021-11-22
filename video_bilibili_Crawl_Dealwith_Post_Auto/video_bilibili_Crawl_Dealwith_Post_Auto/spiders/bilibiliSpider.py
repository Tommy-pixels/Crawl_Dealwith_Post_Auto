import json
import time

import scrapy
from selenium import webdriver
from .. import items
from fake_useragent import UserAgent
from .. import tools

class bilibiliSpider(scrapy.Spider):
    name = "bilibiliSpider"
    start_urls = "https://api.bilibili.com/x/web-interface/search/type?context=&page={}&order=pubdate&keyword=%E8%82%A1%E7%A5%A8&duration=1&tids_2=&from_source=web_search&from_spmid=333.337&platform=pc&__refresh__=true&_extra=&search_type=video&tids=0&highlight=1&single_column=0"
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    # option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--disable-blink-features=AutomationControlled')
    browser = webdriver.Chrome(executable_path="E:\Projects\webDriver\\chrome\\chromedriver.exe", options=option)
    headers = {
        'Host' : 'api.bilibili.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'Origin' : 'https://search.bilibili.com',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    cleaner = tools.cleanCookiesAndHeadersByRow()
    cookies = cleaner.translateCookies(
        "_uuid=9B60CF63-5F25-0BF7-C01D-DAAC25E618A904172infoc; buvid3=BBB4B945-47CD-4E8C-88F7-34C839E28886148828infoc; innersign=0; bsource=search_baidu"
    )
    def start_requests(self):
        for i in range(1,5):
            time.sleep(1)
            url = self.start_urls.format(str(i))
            yield scrapy.Request(url=url, callback=self.parse_videoInfo)

    def parse_videoInfo(self, response, **kwargs):
        videoInfoList = json.loads(response.text)['data']['result']
        for videoInfo in videoInfoList:
            aid = videoInfo['id']  # aid
            duration = videoInfo['duration']    # 视频时长 如 6：09
            check_duration = int(duration.split(':')[0])
            if(check_duration<2 or check_duration>5):
                # 判断时长不符合筛选条件则跳过
                continue
            url_4cid = 'http://www.bilibili.com/video/av' + str(videoInfo['id'])
            temp = tools.getCidBySelenium(self.browser, url_4cid)
            cid = temp[0]  # 获取cid
            cookies = temp[1]
            url_4RealUrl = 'https://api.bilibili.com/x/player/playurl?avid={}&cid={}&qn=16&type=mp4&platform=html5'.format(
                aid,cid
            )
            pubdate = videoInfo['senddate']
            add_para = {}
            add_para['infoItem'] = {
                'title' : videoInfo['title'],
                'bilibiliUrl' : url_4cid,
                'aid' : aid,
                'cid' : cid,
                'pubdate' : pubdate,
                'duration' : duration
            }
            add_para['infoItem']
            yield scrapy.Request(url_4RealUrl, callback=self.parse_videoDownloadable, cb_kwargs=add_para, cookies=cookies, headers=self.headers)
        self.browser.close()

    def parse_videoDownloadable(self, response, infoItem):
        jsonData = json.loads(response.text)
        videoUrl = jsonData['data']['durl'][0]['url']
        videoInfoItem = items.videoInfoItem()
        videoInfoItem['title'] = infoItem['title'].replace('</em>','').replace('<em class="keyword">','')
        videoInfoItem['bilibiliUrl'] = infoItem['bilibiliUrl']
        videoInfoItem['avValue'] = infoItem['aid']
        videoInfoItem['cid'] = infoItem['cid']
        videoInfoItem['videoUrl'] = videoUrl
        videoInfoItem['pubdate'] = infoItem['pubdate']
        videoInfoItem['duration'] = infoItem['duration']
        print("parse_videoDownloadable")
        yield videoInfoItem

