import scrapy
from fake_useragent import UserAgent
from .. import items

class ThepaperSpider(scrapy.Spider):
    name = 'thepaperSpider'
    start_url = [
        'https://www.thepaper.cn/list_page.jsp?nodeid=25434&topContIds=&pageidx=1',     # 10%公司
        'https://www.thepaper.cn/list_page.jsp?nodeid=25435&topContIds=&pageidx=1',     # 金改实验室
        'https://www.thepaper.cn/list_page.jsp?nodeid=25437&topContIds=&pageidx=1'      # 牛市点线面
    ]

    cookies = {
        'acw_tc':'781bad3616423841327372085e4f68fffbc1514a443d99a7dcdf67240c0e2e',
        'UM_distinctid':'17e65b91cb14eb-0e52ee7b74e849-6373264-1fa400-17e65b91cb2ad7',
        'CNZZDATA1261102524':'1747167363-1642375300-https%253A%252F%252Fcn.bing.com%252F%7C1642375300',
        'route':'030e64943c5930d7318fe4a07bfd2a3c; JSESSIONID=4AFAFDA85935675A98AB9F5714371AF2',
        'uuid':'c2b2849e-51d9-4068-85e6-6ba7bd43a268; Hm_lvt_94a1e06bbce219d29285cee2e37d1d26=1642384138',
        'SERVERID':'srv-omp-ali-portal9_80',
        'Hm_lpvt_94a1e06bbce219d29285cee2e37d1d26':'1642384733',
        'ariaDefaultTheme':'undefined'
    }
    headers = {
        'Host': 'www.thepaper.cn',
        'Connection': 'close',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'Accept': 'text/html, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.thepaper.cn/list_25437',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }

    def start_requests(self):
        for url in self.start_url:
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=url, cookies=self.cookies, headers=self.headers, callback=self.parse_articleInfo)

    def parse_articleInfo(self,response):
        articleList = response.xpath("//div[@class='news_li']")
        url_lis = []
        for article in articleList:
            url = 'https://www.thepaper.cn/' + article.xpath('.//h2/a/@href').extract_first()
            title = article.xpath('.//h2/a/text()').extract_first()
            publishTime = article.xpath(".//div[@class='pdtt_trbs']/span/text()").extract_first()
            if('分钟前' in publishTime or '小时前' in publishTime):
                url_lis.append((title, url))
        for url in url_lis:
            add_param = {}
            add_param['title'] = url[0]
            yield scrapy.Request(url=url[1], cookies=self.cookies, headers=self.headers, callback=self.parse_content, cb_kwargs=add_param)

    def parse_content(self, response, title):
        content = ''
        main_node = response.xpath('//div[@class="news_txt"]')
        checkList = main_node.xpath('./*')
        paragraphList = main_node.xpath('./text()').extract()
        _del_list = []
        for check in checkList:
            if(check.xpath('.//@class').extract_first() == 'image_desc'):
                _del_list.append(check.xpath('.//text()').extract_first())
        imgsList = response.xpath('//div[@class="news_txt"]//img/@src').extract()
        hideword = response.xpath('//div[@class="news_txt"]/div[@class="hide_word"]/text()').extract_first()
        articleItem = items.ArticleContentItem()
        if(paragraphList[-2] == hideword):
            paragraphList = paragraphList[:-2]
        for paragraph in paragraphList:
            if(
                    paragraph!=hideword
                    and paragraph.replace(' ', '').replace('\n', '').replace(' ', '') != ''
                    and '来源：' not in paragraph
                    and '（原题' not in paragraph
                    and '（执业证书：' not in paragraph
            ):
                content = content + '<p>' + paragraph + '</p>'
                if(imgsList):
                    content = content + '<img src=\'' + imgsList[0] + '\' />'
                    imgsList.pop(imgsList.index(imgsList[0]))
        content = content.replace('澎湃新闻', '记者')
        # 清除图片注释
        for _del_li in _del_list:
            content = content.replace('<p>'+_del_li+'</p>','')
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem

