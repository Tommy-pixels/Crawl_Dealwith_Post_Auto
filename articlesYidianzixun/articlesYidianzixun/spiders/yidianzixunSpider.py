import json
import scrapy
from fake_useragent import UserAgent
import time
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner



def getCurDate(formatStr: str):
    return time.strftime(formatStr, time.localtime())

def getSecondByDate(date):
    b = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    return time.mktime(b)

class YidianzixunSpider(scrapy.Spider):
    name = 'yidianzixunSpider'

    # start_urls = 'https://a1.go2yd.com/Website/channel/news-list-for-channel?searchentry=channel_navibar&reqid=khjrlfki_1645511221642_181&every_day_history=false&switch_local=false&cstart={}&androidId=262141017d7356c328f8ac0407924537&apiv=030700&cend=30&version=030700&ad_version=010972&group_fromid=g181&yd_device_id=0502d94bdca7e691cd0be03f264112c4c2c4&signature=dy0BT5pzcSNk9Gm-E4CiwX-ha1qcHbwkj5VkgT4Q8S0-_G2wMTQeA0DvevWes46JrdQEbLssyx7S8s4ELW8g_kBcV8YMfHYTL08wVNBgEvnW0x-kekWSVug5H8FdpF7LoU44SdJhHZWa11qEowfONs7fpvLDS6ewKI3rVvfxrAM&eventid=1238799219eec8a968-3dca-43a4-a0c7-38231eb67c04&personalRec=1&infinite=true&distribution=pchomedownload&refresh=1&appid=yidian&os=22&platform=1&cv=6.0.8.4&apk_meta_channel=pchomedownload&fields=docid&fields=date&fields=image&fields=image_urls&fields=like&fields=source&fields=title&fields=url&fields=comment_count&fields=up&fields=down&brand=Android&channel_id=73566788627&cpv=1.211&net=wifi'
    start_urls = 'https://a1.go2yd.com/Website/channel/news-list-for-channel?searchentry=channel_navibar&reqid=khjrlfki_1645520645108_195&every_day_history=false&switch_local=false&cstart={}&androidId=262141017d7356c328f8ac0407924537&apiv=030700&cend=30&version=030700&ad_version=010972&group_fromid=g181&yd_device_id=0502d94bdca7e691cd0be03f264112c4c2c4&signature=aSHOwrU8Vsp8tOwztq_Xqi8il-WUatTnMTAxxbIr-TVv5x8aLlYAgqR6nXFf4_c1SP1sqGASAFlE6b1VWy8-qNUSTJkOhP6onfyLyuZBoeCpmjPYfdZ-yWQ9cg07fw_BPaa_bi8lCkuB5sdoB3EL4SCbsnNxiGk7PZ5z5xwqk3w&eventid=12387992192b962983-e85c-4ebf-8ebf-78913b4da061&personalRec=1&infinite=true&distribution=pchomedownload&refresh=0&appid=yidian&os=22&platform=1&cv=6.0.8.4&apk_meta_channel=pchomedownload&fields=docid&fields=date&fields=image&fields=image_urls&fields=like&fields=source&fields=title&fields=url&fields=comment_count&fields=up&fields=down&brand=Android&channel_id=73566788627&cpv=1.211&net=wifi'

    cookies = {
        'JSESSIONID':'JiUoE7-fIBqqi_GqNr0fYA'
    }
    headers = {
        'Host': 'a1.go2yd.com',
        'Connection': 'close',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/json; charset=utf-8'
    }

    def start_requests(self):
        start_lis = ['0', '10', '20', '30', '40', '50', '60', '70']
        for i in start_lis:
            yield scrapy.Request(self.start_urls.format(i), headers=self.headers, cookies=self.cookies, callback=self.parse_articleList, method='POST')

    def parse_articleList(self, response):
        load_json = json.loads(response.text)
        articleinfo_lis = load_json['result']
        url_list =[]
        for article in articleinfo_lis:
            try:
                publish_time = article['ddate']
            except Exception as e:
                continue
            url = 'https://www.yidianzixun.com/article/{}?s='.format(article['docid'])
            title = article['title']
            if(getCurDate('%Y-%m-%d') in publish_time):
                url_list.append((title, url))

        for url in url_list:
            time.sleep(2)
            if (Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="content-bd"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        if (p_lis[-1].xpath('.//img') != []):
            p_lis = p_lis[:-1]
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first().replace(' ', '').replace('\n','').replace('\t','')
            if (
                '本文作者' in paragraph or '来源' in paragraph or '原文标题' in paragraph or '仅供参考' in paragraph or '一点号作者原创' in paragraph
                    or '未经授权' in paragraph or '不得转载' in paragraph or ('记者' in paragraph and int(len(paragraph.replace('记者',''))<=10))
                    or ('报道' in paragraph and int(len(paragraph.replace('报道',''))<10)) or '文丨' in paragraph or '关注' in paragraph or '责编：' in paragraph
                    or '欢迎留言' in paragraph or '分钟阅读' in paragraph or '源自' in paragraph or '下载并参与' in paragraph or '应用商店搜索' in paragraph or '记者' in paragraph
                    or '编辑' in paragraph or '源：' in paragraph
            ):
                continue
            if(paragraph):
                c = Base_Cleaner.del_content_between(paragraph, s_left='（财联社', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='财联社', s_right='讯')
                c = Base_Cleaner.del_content_between(c, s_left='（来源：', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）讯')
                if (c.startswith('，') or c.startswith(',')):
                    c = c[1:]
                c = cleaner_paragraph.integratedOp(c)
                if(int(len(c))<3):
                    pass
                else:
                    content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'https:' + imgsrc + '\'/>'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem






