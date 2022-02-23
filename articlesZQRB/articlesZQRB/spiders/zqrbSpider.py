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

class ZQRBSpider(scrapy.Spider):
    name = 'zqrbSpider'

    start_urls = 'http://www.zqrb.cn/jrjg/quanshang/index.html'

    cookies = {
        'Hm_lvt_98185f683199e5e5f5b0b21ca82de898':'1645594533',
        'Hm_lpvt_98185f683199e5e5f5b0b21ca82de898':'1645599872',
        'Hm_lvt_6e564fa8a1881e53e017a4197e26db81':'1645593276',
        'Hm_lvt_d6755d6343c132ba403b938388879d14':'1645594490',
        'Hm_lpvt_6e564fa8a1881e53e017a4197e26db81':'1645599935',
        'Hm_lpvt_d6755d6343c132ba403b938388879d14':'1645599935'
    }
    headers = {
        'Host': 'www.zqrb.cn',
        'Connection': 'close',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G973N Build/PPR1.190810.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'http://www.zqrb.cn/jrjg/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    def start_requests(self):
        yield scrapy.Request(self.start_urls, headers=self.headers, cookies=self.cookies, callback=self.parse_articleList)

    def parse_articleList(self, response):
        articleinfo_lis = response.xpath('//div[@class="news_content"]/ul/li')
        url_list =[]
        for article in articleinfo_lis:
            publish_time = article.xpath('./span[@class="date"]/text()').extract_first()
            url = article.xpath('./a[@class="lista"]/@href').extract_first()
            title = article.xpath('./a[@class="lista"]/text()').extract_first()
            if(getCurDate('%Y-%m-%d') in publish_time):
                url_list.append((title, url))
        for url in url_list:
            if (Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], cookies=self.cookies, headers=self.headers,callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        p_lis = response.xpath('//div[@class="content-lcq"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in p_lis:
            paragraph = p.xpath('string(.)').extract_first().replace(' ', '').replace('\n','').replace('\t','').replace(' ', '')
            if (
                '本报记者' in paragraph or '注：' in paragraph or '原文标题' in paragraph or '仅供参考' in paragraph or '数据来源：' in paragraph
            ):
                continue
            if(paragraph):
                c = Base_Cleaner.del_content_between(paragraph, s_left='《证券日报', s_right='》')
                c = Base_Cleaner.del_content_between(c, s_left='证券报', s_right='记者')
                c = Base_Cleaner.del_content_between(c, s_left='（来源：', s_right='）')
                c = Base_Cleaner.del_content_between(c, s_left='（', s_right='）')
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






