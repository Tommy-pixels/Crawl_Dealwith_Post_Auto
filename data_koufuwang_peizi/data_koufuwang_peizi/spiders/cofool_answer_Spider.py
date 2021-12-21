import time

import scrapy, pymysql
from fake_useragent import UserAgent
from ..items import AnswerItem


class CofoolSpider(scrapy.Spider):
    name = 'cofool_answer_Spider'
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
        'Referer': 'http://licai.cofool.com/search/index_wd_%E9%85%8D%E8%B5%84.html?key=069bd3e792316ff6eae7fd9011a3b908'
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
    }

    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="data_usable_database",
        autocommit=True
    )
    cursor = conn.cursor()
    question_url_list = []
    id_lis = [9089]
    for id_ in id_lis:
        cursor.execute('SELECT `id`, `question_url` FROM `data_usable_database`.`tb_cofool_question` WHERE `id`={}'.format(id_))
        question_url = cursor.fetchone()
        question_url_list.append(question_url)

    def start_requests(self):
        # self.question_url_list = self.question_url_list[3821:]
        for question_id, url in self.question_url_list:
            params = {}
            params['question_id'] = question_id
            self.headers['User-Agent'] = UserAgent().random
            self.headers['Hm_lpvt_14678c95555c4a60bf207c106ffb4058'] = str(int(time.time()))
            print(url.replace('.html', '')+'_4_1.html')
            yield scrapy.Request(url=url.replace('.html', '')+'_4_1.html', headers=self.headers, cookies=self.cookies,callback=self.parse_next, cb_kwargs=params)
            time.sleep(2)

    def parse_base(self, response, question_id):
        time.sleep(1)
        num = int(response.xpath('//div[@class="question-result-num"]//span[@class="num"]//text()').extract_first())
        if(num<=20):
            pageNum = 1
        else:
            if(num%20>0):
                pageNum = int(num/20)+1
            else:
                pageNum = int(num/20)
        if(pageNum>1):
            for i in range(2,pageNum):
                next_url = response.url.split('.htm')[0] + '_{}_1.html'.format(str(i))
                params = {}
                params['question_id'] = question_id
                self.headers['User-Agent'] = UserAgent().random
                self.headers['Hm_lpvt_14678c95555c4a60bf207c106ffb4058'] = str(int(time.time()))
                yield scrapy.Request(url=next_url, cookies=self.cookies, headers=self.headers, callback=self.parse_next, cb_kwargs=params)

        liList = response.xpath('.//div[@class="question-result-tab"]//div[@class="parent-answer-div"]')
        answerItem = AnswerItem()
        for li in liList:
            answer = li.xpath(".//div[@class='content-main-rig']//div")[0].xpath("string(.)").extract_first().replace('\r','').replace(' ','')
            answerItem['question_id'] = question_id
            answerItem['answer'] = answer
            answerItem['totle_answer'] = str(num)
            yield answerItem

    def parse_next(self, response, question_id):
        time.sleep(1)
        num = int(response.xpath('//div[@class="question-result-num"]//span[@class="num"]//text()').extract_first())
        liList = response.xpath('.//div[@class="question-result-tab"]//div[@class="parent-answer-div"]')
        answerItem = AnswerItem()
        for li in liList:
            answer = li.xpath(".//div[@class='content-main-rig']//div")[0].xpath("string(.)").extract_first().replace('\r', '').replace(' ', '')
            answerItem['question_id'] = question_id
            answerItem['answer'] = answer
            answerItem['totle_answer'] = str(num)
            yield answerItem

