import scrapy, hashlib, json
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from fake_useragent import UserAgent
from .. import items





class ChinaipoSpider(scrapy.Spider):
    name = 'chinaipoSpider'
    start_urls = [
        'https://www.chinaipo.com/ipo/',
        'https://www.chinaipo.com/hk/',
        'https://www.chinaipo.com/usstock/',
        'https://www.chinaipo.com/mvm/',
        'https://www.chinaipo.com/newstock/',
        'https://www.chinaipo.com/xiaoipo/',
        'https://www.chinaipo.com/kechuangban/'
    ]

    headers = {
        'Host': 'www.chinaipo.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json;charset=utf-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.chinaipo.com/newstock/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    cookies = {
        '__yjs_duid':'1_3aab3ab0e27f03776a51afebd1c6c8cb1640656737489',
        'PHPSESSID':'v2pot5iekc042spcsuccc0ab61',
        'XSBlang':'zh-cn',
        'UM_distinctid':'17dfec31d38272-067b69c47b1247-6373264-1fa400-17dfec31d39c93',
        'CNZZDATA1255725096':'6281471-1640646185-%7C1640646185',
        'Hm_lvt_61a2d81fc23a3a8087c8791bf55f7e6e':'1640656740',
        'Hm_lpvt_61a2d81fc23a3a8087c8791bf55f7e6e':'1640656968'
    }

    def start_requests(self):
        for url in self.start_urls:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.article_info,
            )

    def article_info(self, response):
        articlelis = response.xpath('//div[@class="l-tabs-panel"]/div[@class="c-tabPanel__wrapper"]/div[@class="news__item hoverLarger"]')
        url_lis = []
        for article in articlelis:
            title = article.xpath('.//h5/a/text()').extract_first()
            article_url = article.xpath('.//h5/a/@href').extract_first()
            publish_time = article.xpath('.//div[@class="news__time"]/text()').extract_first().replace('-','')
            if(Contraler_Time.getCurDate(formatStr='%Y%m%d') == publish_time):
                if((title, article_url) not in url_lis):
                    url_lis.append((title, article_url))
        cb_p = {}
        for article_item in url_lis:
            cb_p['title'] = article_item[0]
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(
                url=article_item[1],
                headers=self.headers,
                cookies=self.cookies,
                callback=self.article_content,
                cb_kwargs=cb_p
            )

    def article_content(self, response, title):
        content = ''
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath('//div[@class="c-article__detail"]/*')
        for p in pList:

            c = "".join(p.xpath('string(.)').extract()).replace('\n','').replace('\r', '').replace('\t', '')
            if(c!='' and '来源:' not in c and '头图来源' not in c and '转载声明' not in c and '风险提示' not in c and '关键词'not in c and '声明：' not in c and '本文来源：' not in c):
                content = content + "<p>" + c + "</p>"
            if(p.xpath('.//img')!=[]):
                for img in p.xpath('.//img'):
                    imgsrc = img.xpath('.//@src').extract_first()
                    content = content + '<img src=\'https://www.chinaipo.com' + imgsrc + '\'/>'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem


