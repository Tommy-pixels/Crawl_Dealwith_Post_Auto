import time

import scrapy
from fake_useragent import UserAgent
from ..items import QuestionItem

class CofoolSpider(scrapy.Spider):
    name = 'cofool_question_Spider'
    start_url = 'http://licai.cofool.com/search/index_wd_%E9%85%8D%E8%B5%84_key_069bd3e792316ff6eae7fd9011a3b908_p_{}.html'
    page = 1
    headers = {
        'Host': 'licai.cofool.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    cookies = {
        'viewNotice' : '1',
        '_uab_collina' : '163823306951619245118957',
        'url_city_str' : 'aid_35',
        'url_city_str_' : '35',
        'PHPSESSID' : 'bv2qim2ougj73hf3r7c8e1t892',
        'Hm_lvt_14678c95555c4a60bf207c106ffb4058' : '1638233070, 1638236178',
        'think_language' : 'zh-CN',
        'cur_city' : '%E4%BD%9B%E5%B1%B1',
        'cur_cityid' : '35',
        'cur_relatedid' : '30',
        'cur_parentid' : '4',
        'locate' : '0',
        'Hm_lpvt_14678c95555c4a60bf207c106ffb4058' : '1638237451'
    }

    def start_requests(self):
        for i in range(1, 1251):
            url = self.start_url.format(
                str(i)
            )
            self.headers['User-Agent'] = UserAgent().random
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse)
            time.sleep(1)

    def parse(self, response):
        liList = response.xpath("//div[@class='answer-type-cont']//div//a[@class='answer-detail-title c333']")
        questionItem = QuestionItem()
        for li in liList:
            tag = '配资'
            question = li.xpath(".//text()").extract_first()
            page_url = response.url
            question_url = 'http://licai.cofool.com' + li.xpath(".//@href").extract_first()
            questionItem['tag'] = tag
            questionItem['question'] = question
            questionItem['page_url'] = page_url
            questionItem['question_url'] = question_url
            yield questionItem





