import json, time
import scrapy
from .. import items
from fake_useragent import UserAgent


# 获取当前日期
def getCurDate(form="%Y%m%d"):
    return time.strftime(form, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)


class StockstarSpider(scrapy.Spider):
    name = 'futuniuniuSpider'
    start_url = 'https://q.futunn.com/nnq/list-feed?relation_type=0&feed_mark={}&more_mark={}&refresh_type=1&_=1644384946145'

    cookies = {
        'uid':'30985997',
        'web_sig':'JmygG207lv%2B4P%2Fvi97RqNuVKa%2FJ1N%2B8q%2BsMNDNvNrc4t%2F%2F6NtA3wSNVBnIMOx%2F%2Fm1qr6lt4MY4ZdIpyVKQTIv0CnAbGu20dkuVJHryDHm8BloSw0JO%2BzYIY65A1Wg%2FyO;'
    }
    headers = {
        'Host': 'q.futunn.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://q.futunn.com/nnq?lang=zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9'
    }
    times = 1
    max_times = 30
    def start_requests(self):
        yield scrapy.Request(url=self.start_url.format('',''), headers=self.headers, cookies=self.cookies, callback=self.parse_comment)

    def parse_comment(self, response):
        commentItem = items.CommentItem()
        data = json.loads(response.text)['data']
        more_mark = data['more_mark']
        comment_lis = data['feed']
        for comment in comment_lis:
            # 评论
            rich_text_lis = comment['summary']['rich_text']
            # 对评论的回复
            comment_items = comment['comment']['comment_items']
            publishTime = comment['common']['timestamp']
            if(publishTime < int(getSecondByDate(getCurDate()+' 00:00:00'))):
                continue
            comments = []
            content0 = ''
            content1 = ''
            # 评论
            if(rich_text_lis):
                for c_i1 in rich_text_lis:
                    if(c_i1['type']!=0):
                        continue
                    else:
                        if('<br/>' not in c_i1['text']):
                            content0 = content0 + c_i1['text']
                if (content0 != ''):
                    comments.append(content0)
                content0 = ''

            # 评论有回复
            if(comment_items):
                for c_i2 in comment_items:
                    text_lis2 = c_i2['rich_text_items']
                    if(text_lis2):
                        for c_i2_item in text_lis2:
                            if(c_i2_item['type']!=0):
                                continue
                            else:
                                if ('<br/>' not in c_i2_item['text']):
                                    content1 = content1 + c_i2_item['text']
                if(content1!=''):
                    comments.append(content1)
                content1 = ''
            commentItem['publishTime'] = publishTime
            commentItem['comment'] = comments
            yield commentItem
        if(self.times!=self.max_times):
            self.times = self.times + 1
            yield scrapy.Request(url=self.start_url.format(more_mark, more_mark), headers=self.headers, cookies=self.cookies, callback=self.parse_comment)
            time.sleep(0.5)
