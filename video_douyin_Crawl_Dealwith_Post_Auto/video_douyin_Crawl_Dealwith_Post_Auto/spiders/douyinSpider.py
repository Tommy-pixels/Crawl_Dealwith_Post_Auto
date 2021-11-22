import sys
sys.path.append(r"E:\Projects")
import scrapy,time, json
from packageDIY.globalTools import douyinCrack
from packageDIY.videoRef.DatabaserOperator import databaseOperator
from .. import items

from fake_useragent import UserAgent

class DouyinSpider(scrapy.Spider):
    name = 'douyinSpider'
    'https://www.douyin.com/aweme/v1/web/search/item/?device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_video_web&sort_type=0&publish_time=0&keyword=g&search_source=normal_search&query_correct_type=1&is_filter_search=0&offset=0&count=30&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F91.0.4472.124+Safari%2F537.36&browser_online=true&msToken=FBzPVQsX21XqA10zJ7kRdP_W0HzALIWvlvDbb8qjOWz6IM4o6z3gacWwGDl4JlxyTpM9UxDM7iYEPCjn7sdAJpuz6ZmDf55eRb7YhZUA7DQYMpKIlVKNnTI=&X-Bogus=DFSzswSYuZ0ANxAgS7-7FN4ELVV5&_signature=_02B4Z6wo00001LxdDOwAAIDDDKzgJu4I0BS8WQhAAE6KognSPGpcjOUyxYrpUP-7rDBzK2.zRWpbfYW9TnnDDADbzYkdYy.5Bs.e0lhVC038UegbRmgmMaEanOM.NysSK2a3QHUeIt59qYXy4e '
    SEARCH_API = 'https://www.douyin.com/aweme/v1/web/search/item/?device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_video_web&sort_type=2&publish_time=1&keyword={}&search_source=normal_search&query_correct_type=1&is_filter_search=1&offset={}&count={}&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name={}&browser_version={}&browser_online=true&msToken={}&X-Bogus=DFSzswSYuZ0ANxAgS7-7FN4ELVV5&_signature=_02B4Z6wo00001LxdDOwAAIDDDKzgJu4I0BS8WQhAAE6KognSPGpcjOUyxYrpUP-7rDBzK2.zRWpbfYW9TnnDDADbzYkdYy.5Bs.e0lhVC038UegbRmgmMaEanOM.NysSK2a3QHUeIt59qYXy4e '
    '''&X-Bogus={}&_signature={}'''
    KEY_WORD = {
        '股': '%E8%82%A1',
        '股票': "%E8%82%A1%E7%A5%A8",
        '涨跌': "%E6%B6%A8%E8%B7%8C",
        '大盘': "%E5%A4%A7%E7%9B%98",
        'B股': "B%E8%82%A1",
        '短线': "%E7%9F%AD%E7%BA%BF",
        '指数': "%E6%8C%87%E6%95%B0"
    }
    URL_PARAMS = {
        'keyword': '%E8%82%A1',  # 搜索关键词
        'offset': '0',   # 滚动距离
        'count' : '24',
        'browser_name' : 'Mozilla',    # 跟请求头一样
        'browser_version' : '5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F91.0.4472.124+Safari%2F537.36', # 跟请求头一样
        'msToken' : '', # 由服务器返回
        'X-Bogus' : '',
        '_signature' : '',  # 本地生成
    }
    HEADERS = {
        'Host': 'www.douyin.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': '',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    start_url = SEARCH_API.format(
        URL_PARAMS['keyword'],
        URL_PARAMS['offset'],
        URL_PARAMS['count'],
        URL_PARAMS['browser_name'],
        URL_PARAMS['browser_version'],
        URL_PARAMS['msToken']
    )
    dbOperator = databaseOperator.dbOperator(databaseName='videodatabase')

    captchaPath = 'E:\\assets\\captcha\\'
    cracker = douyinCrack.DouyinCrack(driverPath=r'E:\Projects\webDriver\\chrome\\chromedriver.exe',
                                      captchaDstDirPath=captchaPath)
    cracker.del_all_cookies()
    url = 'https://www.douyin.com/search/{}'.format('%E8%82%A1')
    cracker.enter_url(url)
    time.sleep(2)
    cookies = cracker.handle_SlideCheck()
    cracker.closeBrowser()

    def start_requests(self):
        for keyword in self.KEY_WORD.values():
            self.URL_PARAMS['msToken'] = self.cookies['msToken']

            ua =  UserAgent().random
            h = ua.split(' ')[0].split('/')[0]
            v = ua.split(' ')[0].split('/')[1] + '+' + ua.split(ua.split(' ')[0])[1].strip()
            self.URL_PARAMS['browser_name'] = h
            self.URL_PARAMS['browser_version'] = v
            self.HEADERS['User-Agent'] = ua
            self.HEADERS['Referer'] = 'https://www.douyin.com/search/{}?publish_time=1&sort_type=2&source=normal_search&type=video'.format(keyword)
            self.start_url = self.SEARCH_API.format(
                keyword,
                self.URL_PARAMS['offset'],
                self.URL_PARAMS['count'],
                self.URL_PARAMS['browser_name'],
                self.URL_PARAMS['browser_version'],
                self.URL_PARAMS['msToken']
            )
            time.sleep(2)
            yield scrapy.Request(url=self.start_url, cookies=self.cookies, headers=self.HEADERS, callback=self.parse_)

    def parse_(self, response):
        data = json.loads(response.body)
        print(data)
        # data = json.loads(response.text)['data']
        # videoItem = items.VideoItem()
        # for videoInfo in data:
        #     title = videoInfo['aweme_info']['desc']
        #     url = videoInfo['aweme_info']['video']['play_addr_lowbr']['url_list'][0]
        #     publishTime = videoInfo['aweme_info']['create_time']
        #     duration = videoInfo['aweme_info']['video']['duration']
        #     videoItem['title'] = title
        #     videoItem['url'] = url
        #     videoItem['publishTime'] = publishTime
        #     videoItem['duration'] = duration
        #     yield videoItem

