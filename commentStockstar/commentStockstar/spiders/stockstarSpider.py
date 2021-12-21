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
    name = 'stockstarSpider'
    start_url = 'http://t.stockstar.com/live/index?skip={}&page={}&json=true&pagesize=5'

    cookies = {
        'Hm_lvt_d2eddf9b155bdbd9ea015490aef570fa':'1640054180',
        'isPop':'1',
        'Hm_lpvt_d2eddf9b155bdbd9ea015490aef570fa':'1640055191'
    }
    headers = {
        'Host': 't.stockstar.com',
		'Connection': 'close',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'User-Agent': str(UserAgent().random),
		'X-Requested-With': 'XMLHttpRequest',
		'Referer': 'http://t.stockstar.com/',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    def start_requests(self):
        for i in range(1, 18):
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=self.start_url.format(str(i*5+2), str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_comment)

    def parse_author(self, response):
        pass

    def parse_comment(self, response):
        data = json.loads(response.text)['data']
        commentItem = items.CommentItem()
        live_author_lis = []
        for comment in data:
            sequence = comment['sequence']
            live_url = 'http://t.stockstar.com/Live/LiveRoom/' + str(sequence)
            if(live_url not in live_author_lis):
                live_author_lis.append(live_url)

            content = comment['content']
            publishTime = comment['ctime'].split('(')[1].split(')')[0]
            yesterdaySeconds = int(getSecondByDate(str(getCurDate()) + ' 00:00:00'))*1000 - 172800*1000  # 48h前的时间戳（秒）
            if (int(publishTime) < int(yesterdaySeconds)):
                continue
            if('<' in content or '>' in content):
                if (content.split('>')[1].split('<')[0] == ''):
                    continue
                commentItem['comment'] = content.split('>')[1].split('<')[0]
            else:
                if(content==''):
                    continue
                commentItem['comment'] = content
            commentItem['publishTime'] = publishTime
            yield commentItem

        for live_url_item in live_author_lis:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(live_url_item, cookies=self.cookies, headers=self.headers, callback=self.parse_live_comment)

    def parse_live_comment(self,response):
        li_lis = response.xpath('//ul[@id="messagelist"]/li')
        commentItem = items.CommentItem()
        for li in li_lis:
            publishTime = li.xpath('.//span[@class="fl"]/text()').extract_first().replace('月', '').replace('日', '')
            content = li.xpath('.//span[@class="fr Msgdetail_list_fr"]')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ', '')
            if(getCurDate(form="%m%d")!=publishTime):
                continue
            commentItem['publishTime'] = publishTime
            commentItem['comment'] = content
            yield commentItem