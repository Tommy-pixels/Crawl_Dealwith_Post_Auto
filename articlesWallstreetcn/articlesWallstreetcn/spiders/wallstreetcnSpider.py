import json
import scrapy
from fake_useragent import UserAgent
import bs4
from .. import items
from auto_datahandler.basement__.ContralerTime import Contraler_Time
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier


class WallstreetcnSpider(scrapy.Spider):
    name = 'wallstreetcnSpider'
    API_Next = 'https://api-one.wallstcn.com/apiv1/content/information-flow?channel=shares&accept=article&cursor={}&limit=20&action=upglide'
    start_urls = [
        'https://api-one.wallstcn.com/apiv1/content/information-flow?channel=shares&accept=article&limit=20&action=upglide'
    ]

    cookies = {
        'Hm_lvt_c9477ef9d8ebaa27c94f86cc3f505fa5':'1642037635',
        'taotieDeviceId':'17e5111e-74ca-564b-819d-9d0c5dbab98e',
        '_ga':'GA1.1.2086072011.1642037635',
        'Hm_lpvt_c9477ef9d8ebaa27c94f86cc3f505fa5':'1642037654',
        '_ga_4VH50R2B8W':'GS1.1.1642037635.1.1.1642038195.0'
    }
    headers = {
        'Host': 'wallstreetcn.com',
        'Connection': 'close',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode':' navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://wallstreetcn.com/news/shares',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    headers_api = {
        'Host': 'api-one.wallstcn.com',
        'Connection': 'close',
        'x-taotie-device-id': '17e5111e-74ca-564b-819d-9d0c5dbab98e',
        'x-track-info': '{"appId":"com.wallstreetcn.web","appVersion":"0.37.12"}',
        'sec-ch-ua-mobile': '?0',
        'x-ivanka-app': 'wscn|web|0.37.12|0.0|0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'x-client-type': 'pc',
        'x-ivanka-platform': 'wscn-platform',
        'x-device-id': '17e5111e-74ca-564b-819d-9d0c5dbab98e',
        'Accept': '*/*',
        'Origin': 'https://wallstreetcn.com',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://wallstreetcn.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    def start_requests(self):
        for url in self.start_urls:
            self.headers_api['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url, headers=self.headers_api, callback=self.parse_articleList)

    def parse_articleList(self, response):
        load_json = json.loads(response.text)['data']
        articleinfo_lis = load_json['items']
        url_list =[]
        for article in articleinfo_lis:
            publish_time = article['resource']['display_time']
            url = article['resource']['uri']
            title = article['resource']['title']
            if(publish_time > Contraler_Time.getSecondByDate(Contraler_Time.getCurDate('%Y%m%d') + ' 00:00:00')):
                url_list.append((title, url))

        for url in url_list:
            if (Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], callback=self.parse_articleContent, cb_kwargs=add_param)


    def parse_next(self,response):
        load_json = json.loads(response.text)['data']
        articleinfo_lis = load_json['items']
        url_list = []
        for article in articleinfo_lis:
            publish_time = article['resource']['display_time']
            url = article['resource']['uri']
            title = article['resource']['title']
            if (publish_time > Contraler_Time.getSecondByDate(Contraler_Time.getCurDate('%Y%m%d') + ' 00:00:00')):
                url_list.append((title, url))

        for url in url_list:
            if(Base_Identifier.is_intterrogative(url[0])):
                self.headers['User-Agent'] = str(UserAgent().random)
                add_param = {}
                add_param['title'] = url[0]
                yield scrapy.Request(url[1], callback=self.parse_articleContent, cb_kwargs=add_param)

    def parse_articleContent(self, response, title):
        articleItem = items.ArticleItem()
        article = response.text.split('<article')[-1].split('</article>')[0].split('class="rich-text">')[-1]
        soup = bs4.BeautifulSoup(article)
        p_lis = soup.find_all('p')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in p_lis:
            paragraph = p.text.replace(' ', '').replace('\n','').replace('\t','')
            if(paragraph):
                c = cleaner_paragraph.integratedOp(paragraph)
                content = content + '<p>' + c + '</p>'
            try:
                has_img = p.find('img')
            except Exception as e:
                has_img = False
            if(has_img):
                content = content + '<img src = \'' + has_img.get('src') + '\' />'
        articleItem['title'] = title
        articleItem['content'] = content
        yield articleItem






