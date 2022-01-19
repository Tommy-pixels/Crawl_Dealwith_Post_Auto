import scrapy, hashlib, json
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from .. import items
from auto_datahandler.customFunction__.Cleaner.base_cleaner import Base_Cleaner
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier

def sha1(s):
    if(not isinstance(s, bytes)):
        text = bytes(s, 'utf-8')
    sha = hashlib.sha1(text)
    encrypts = sha.hexdigest()
    return encrypts

def md5(s):
    return hashlib.md5(s.encode(encoding='utf-8')).hexdigest()

def get_sign(s):
    return md5(sha1(s))



class CailiansheSpider(scrapy.Spider):
    name = 'cailiansheSpider'
    start_urls = 'https://www.cls.cn/v3/depth/list/1000?'

    headers = {
        'Host': 'www.cls.cn',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json;charset=utf-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.cls.cn/depth?id=1000',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = {
        'HWWAFSESID': 'de299127461c03f35cf',
        'HWWAFSESTIME': '1639530458358',
        'Hm_lvt_fa5455bb5e9f0f260c32a1d45603ba3e': '1639530465',
        'vipNotificationState': 'on',
        'hasTelegraphRemind': 'on',
        'hasTelegraphSound': 'on',
        'hasTelegraphNotification': 'off',
        'Hm_lpvt_fa5455bb5e9f0f260c32a1d45603ba3e': '1639534374'
    }
    keyparams = 'app=CailianpressWeb&id=1000&last_time={}&os=web&rn=20&sv=7.7.5'
    today = int(Contraler_Time.getSecondByDate(Contraler_Time.getCurDate("%Y%m%d")+ " 00:00:00"))

    def start_requests(self):
        paramstr = self.keyparams.format('')
        sign=get_sign(self.keyparams.format(''))
        yield scrapy.Request(
            url=self.start_urls + paramstr + '&sign=' + sign,
            headers=self.headers,
            cookies=self.cookies,
            callback=self.article_info,
        )

    def article_info(self, response):
        datalis = json.loads(response.text)['data']
        last_ctime = datalis[-1]['ctime']
        next_url = ''
        articlelis = []
        for article in datalis:
            title = article['title']
            article_url = 'https://www.cls.cn/detail/' + str(article['id'])
            publish_time = article['ctime']
            if(int(publish_time) > self.today):
                articlelis.append((title, article_url))
        cb_p = {}
        for article_url in articlelis:
            if (Base_Identifier.is_intterrogative(article_url[0])):
                cb_p['title'] = article_url[0]
                yield scrapy.Request(
                    url=article_url[1],
                    headers=self.headers,
                    cookies=self.cookies,
                    callback=self.article_content,
                    cb_kwargs=cb_p
                )

        if(last_ctime>int(Contraler_Time.getSecondByDate(Contraler_Time.getCurDate("%Y%m%d")+ " 00:00:00"))):
            paramstr = self.keyparams.format(last_ctime)
            sign = get_sign(self.keyparams.format(last_ctime))
            yield scrapy.Request(
                url=self.start_urls + paramstr + '&sign=' + sign,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.article_info
            )

    def article_content(self, response, title):
        content = ''
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath("//div[@class='m-b-40 detail-content ']//div['m-b-10']/*")
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = "".join(p.xpath('string(.)').extract())
            if(c!=''):
                c = Base_Cleaner.del_content_between(c, s_left='（财联社', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='财联社', s_right='讯')
                c = Base_Cleaner.del_content_between(c, s_left='（来源：', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）讯')
                if (c.startswith('，') or c.startswith(',')):
                    c = c[1:]
                c = cleaner_paragraph.integratedOp(c)
                content = content + "<p>" + c + "</p>"
            if(p.xpath('.//img')!=[]):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'' + imgsrc + '\'/>'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


