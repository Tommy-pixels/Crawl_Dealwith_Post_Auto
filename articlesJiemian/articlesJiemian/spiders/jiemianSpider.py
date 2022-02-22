import scrapy, time, json
import bs4
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier

# 获取当前日期
def getCurDate(format='%Y%m%d'):
    return time.strftime(format, time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

class JiemianSpider(scrapy.Spider):
    name = 'jiemianSpider'
    start_url = 'https://a.jiemian.com/index.php?m=newLists&a=loadMore&callback=jQuery110208336617447512662_1645432410522&tid={}&page={}&tpl=sub-list&repeat=7118479%2C7105964%2C7104124&list_type=&_=1645432410528'
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    cookies = {
        'SERVERID':'10.70.50.76',
        '__utrace':'fb3a3968f08a47cd563d502817327b3a'
    }

    def start_requests(self):
        tid_lis = ['1461', '525', '315']
        for tid in tid_lis:
            for i in range(1,2):
                self.headers['Host'] = 'a.jiemian.com'
                self.headers['Sec-Fetch-Site'] = 'same-site'
                self.headers['Sec-Fetch-Mode'] = 'no-cors'
                self.headers['Sec-Fetch-User'] = '?1'
                self.headers['Sec-Fetch-Dest'] = 'script'
                self.headers['Referer'] = 'https://www.jiemian.com/'
                self.headers['Accept'] = '*/*'
                self.headers['User-Agent'] = str(UserAgent().random)
                yield scrapy.Request(url=self.start_url.format(tid, str(i)), headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        start_char = response.text.find('{')
        end_char = response.text.find('}')
        html = json.loads('{' + response.text[start_char+1:end_char] + '}')['html']
        bs_html = bs4.BeautifulSoup(html)
        li_lis = bs_html.find_all('li')
        urlList = []
        for li in li_lis:
            publishTime = li.find('span', attrs={'class':'news-footer__date'}).text
            if('今天' not in publishTime):
                continue
            title = li.find('h3').text
            url = li.find('h3').parent.get('href')
            if (Base_Identifier.is_intterrogative(title) and url not in urlList):
                urlList.append(url)
        for url in urlList:
            self.headers['Host'] = 'www.jiemian.com'
            self.headers['Sec-Fetch-Site'] = 'same-origin'
            self.headers['Sec-Fetch-Mode'] = 'navigate'
            self.headers['Sec-Fetch-User'] = '?1'
            self.headers['Sec-Fetch-Dest'] = 'document'
            self.headers['Cache-Control'] = 'max-age=0'
            self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            self.headers['Referer'] = 'https://www.jiemian.com/lists/112.html'
            cookies_ = {
                # '__utrace':'fb3a3968f08a47cd563d502817327b3a',
                # 'br-client':'7d8ca0ae-a218-44bf-85e5-9c47e4967667',
                # 'br-resp-key':'"g:220221171934a5700000008482447a8909"',
                # 'br-session-74':'25ce6229-e5f7-4167-8e6a-fb42ea591143|1645433558745|{}|123'.format(str(int(time.time()*1000)))
            }
            yield scrapy.Request(url=url, headers=self.headers, cookies=cookies_, callback=self.parse_content)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        title = response.xpath('//h1')[0].xpath('string(.)').extract_first().replace('\n', '').replace(' ','')
        pList = response.xpath('//div[@class="article-content"]/*')
        pList = pList[1:]
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '')
            if (c != ''):
                c = cleaner_paragraph.integratedOp(c)
                content = content + '<p>' + c + '</p>'
            if (p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + '<img src=\'' + img.xpath('./@src').extract_first() + '\' />'

        articleContentItem['title'] = title
        articleContentItem['content'] = content
        yield articleContentItem

