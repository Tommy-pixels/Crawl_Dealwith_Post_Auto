import scrapy
from fake_useragent import UserAgent
import json
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from .. import items
import time

class AigupiaoSpider(scrapy.Spider):
    name = 'aigupiaoSpider'
    GET_MD_URL = 'https://www.aigupiao8.com'
    start_url = 'https://www.aigupiao8.com/Api/LiveMsg/hot_msg?act=popular_content&source=pc&page={}&before_express_score=0'
    md = ''
    API_COMMENT = 'https://www.aigupiao.com/index.php?s=/Api/Comment/comment_list&kind={}&id={}&md={}&before={}'
    headers = {
        'Connection': 'close',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.aigupiao8.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    cookies = {
        'PHPSESSID':'8e1ca473feafd9bb78703e72f773327c',
        'Hm_lvt_693ae2f38bfa31bae3f0cc7ca5b89432':'1643246260',
        'Hm_lpvt_693ae2f38bfa31bae3f0cc7ca5b89432':'1643246810'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.GET_MD_URL, headers=self.headers, cookies=self.cookies,callback=self.parse_md)


    def parse_md(self, response):
        """
        获取md值,发起请求
        :param response:
        :return:
        """
        self.md = response.text.split(' md = "')[-1].split('";')[0]
        for i in range(1, 7):
            time.sleep(2)
            self.headers['Host'] = 'www.aigupiao8.com'
            yield scrapy.Request(url=self.start_url.format(str(i)), headers=self.headers, cookies=self.cookies,callback=self.parse_info)


    def parse_info(self,response):
        json_data = json.loads(response.text)
        data_lis = json_data['data_list']
        msg_id_lis = []
        for msg in data_lis:
            rec_time = int(msg['msg']['rec_time'])
            if(rec_time>=int(Contraler_Time.getSecondByDate(Contraler_Time.getCurDate('%Y%m%d') + ' 00:00:00'))):
                msg_id_lis.append(msg['msg']['id'])
        for msg_id in msg_id_lis:
            time.sleep(2)
            self.headers['Host'] = 'www.aigupiao.com'
            self.headers['Origin'] = 'https://www.aigupiao8.com'
            dic = {}
            dic['msg_id'] = msg_id
            yield scrapy.Request(url=self.API_COMMENT.format('live_msg', msg_id, self.md,''), cookies=self.cookies, headers=self.headers,callback=self.parse_comment, cb_kwargs=dic)

    def parse_comment(self, response, msg_id):
        commentItem = items.CommentItem()
        data_json = json.loads(response.text)
        before = data_json['before']
        comment_lis = data_json['comment_list']
        for comment in comment_lis:
            sub_list = []
            if(comment['sub_list']):
                for sub_comment in comment['sub_list']:
                    sub_list.append((sub_comment['content'], sub_comment['sort_time']))
            content = comment['content']
            rec_time = comment['rec_time']
            commentItem['comment'] = content
            commentItem['publishTime'] = rec_time
            commentItem['sub_list'] = sub_list
            yield commentItem

        if(before!='0'):
            self.headers['Host'] = 'www.aigupiao.com'
            self.headers['Origin'] = 'https://www.aigupiao8.com'
            dic = {}
            dic['msg_id'] = msg_id
            yield scrapy.Request(url=self.API_COMMENT.format('live_msg', msg_id, self.md,before), cookies=self.cookies,headers=self.cookies,callback=self.parse_comment, cb_kwargs=dic)