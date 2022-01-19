import bs4
import scrapy, time
from fake_useragent import UserAgent
from .. import items
import execjs, re
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.customFunction__.Identifier.base_identifier import Base_Identifier

# 获取当前日期
def getCurDate(format="%Y%m%d"):
    return time.strftime(format, time.localtime())

# 返回指定日期时间戳 时间格式 '%Y%m%d %H:%M:%S' 20210924 00：00：00 该方法用于哔哩哔哩时间的判断
def getSecondByDate(date):
    b = time.strptime(date, '%Y%m%d %H:%M:%S')
    return time.mktime(b)

def execute_jsfile(filepath=r'E:\Projects\Crawl_Dealwith_Post_Auto\articlesCfi\articlesCfi\decode.js'):
    js = '''function decode(s){return unescape(s.replace(/~/g,'%u'))}'''
    js_executor = execjs.compile(js)
    return js_executor

class NbdSpider(scrapy.Spider):
    name = 'cfiSpider'
    start_url = 'https://industry.cfi.cn/BCA0A4127A4128A4132.html'
    headers = {
        'Host': 'industry.cfi.cn',
        'Connection': 'close',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Referer': 'https://industry.cfi.cn/BCA0A4127A4128A4133.html',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'ASP.NET_SessionId':'2fn4zrqo5wbxfv45v2aiuk55',
        'cficA0A4127A4128A4131':'2021-12-23'
    }

    def start_requests(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        self.cookies['cficA0A4127A4128A4131'] = getCurDate(format="%Y-%m-%d")
        yield scrapy.Request(url=self.start_url, headers=self.headers, cookies=self.cookies, callback=self.parse_articleInfo)

    def parse_articleInfo(self, response):
        li_lis = response.xpath("//div[@class='zidiv2']/a")
        urlList = []
        today = getCurDate(format='%m%d')
        for article in li_lis:
            try:
                publishTime = article.xpath("./@href").extract_first().split(today)
                if(len(publishTime)==1):
                    continue
            except:
                continue
            # url = 'https://industry.cfi.cn/' + article.xpath("./@href").extract_first()
            url = article.xpath("./@href").extract_first()
            title = article.xpath("./text()").extract_first()
            if (url not in urlList):
                urlList.append((url, title))

        for url in urlList:
            if (Base_Identifier.is_intterrogative(url[1])):
                dic = {}
                dic['title'] = url[1]
                yield scrapy.Request(
                    url='https://industry.cfi.cn/newspage.aspx?id={}'.format(url[0].split('.')[0].replace('p', '')),
                    headers=self.headers, cookies=self.cookies,
                    callback=self.parse_content,
                    cb_kwargs=dic
                )

    def parse_content(self, response, title):
        articleContentItem = items.ArticleContentItem()
        cleaner_paragraph = Cleaner_Paragraph()
        try:
            # s = response.text.split('var nr{}="'.format(response.url.split('.')[1].split('.')[0]))[1].split('"')[0]
            s = response.text.split('var nr{}="'.format(response.url.split('.')[-1].split('=')[-1]))[1].split('"')[0]
            executor = execute_jsfile()
            res = executor.call('decode', s)
            soup = bs4.BeautifulSoup(res, features="lxml")
            try:
                title_ = soup.h1.text
            except Exception as e:
                title_ = title
                pass
            img_lis = []
            for img in soup.find_all('img'):
                img_lis.append(img.get('src'))
            pList = res.split('<!--newstext-->')[1].split('<!--/newstext-->')[0].split('<br />')
            content = ''
            if (len(img_lis) > 0 and len(img_lis) < len(pList)):
                img_i = 0
            for p in pList:
                if (p != ""):
                    c = re.sub(u"\\<.*?\\>", "", p).replace('\u3000', '')
                if ('扫描下方二维码' in c):
                    break
                if (c != '' and '每经编辑：' not in c and '来源：' not in c and '仅供参考' not in c and '编辑：' not in c
                        and '记者：' not in c and '声明：' not in c and '排版：' not in c and '视觉：' not in c and '封面：' not in c and '整理：' not in c
                        and '每经记者' not in c and ' 每经编辑' not in c and ' 每经评论员' not in c and '编辑' not in c and '校对' not in c and '封面图' not in c
                ):
                    c = cleaner_paragraph.integratedOp(c.replace('\n', '').replace(' ','').replace('\u3000', ''))
                    content = content + '<p>' + c + '</p>'
                if (img_lis != []):
                    content = content + '<img src=\'' + img_lis[0] + '\' />'
                    img_lis.pop(0)

            articleContentItem['title'] = title_
            articleContentItem['content'] = content
            yield articleContentItem
        except:
            tdcontent = response.xpath('//div[@id="tdcontent"]')
            try:
                title_ = tdcontent.xpath('h1')[0].xpath('string(.)').extract_first().replace(' ', '')
            except Exception as e:
                try:
                    title_ = tdcontent.xpath('h1/text()').extract_first().replace(' ', '')
                except Exception as e:
                    title_ = title
            content = ''
            try:
                p_lis = tdcontent.extract_first().split('<!--newstext-->')[1].split('<!--/newstext-->')[0].split('<br>')
                for p in p_lis:
                    if('+newspiclink+"' in p):
                        imgsrc = 'https://img.cfi.cn/readpic.aspx?imageid=' + "".join(re.findall('\d+', p.split('<script>')[1].split('</script>')[0]))
                        c = re.sub(u"\\<script>.*?\\</script>", "", p).replace('\u3000', '')
                        if(c.replace('\r', '').replace('\n', '').replace('\u3000', '')!=''):
                            c = cleaner_paragraph.integratedOp(re.sub(u"\\<.*?\\>", "",c.replace('\r', '').replace('\n', '').replace('\u3000', '')))
                            content = content + '<p>' + c + '</p>' + '<img src=\'' + imgsrc + '\'/>'
                        else:
                            content = content + '<img src=\'' + imgsrc + '\'/>'
                    else:
                        c = re.sub(u"\\<script>.*?\\</script>", "", p).replace('\u3000', '')
                        c = cleaner_paragraph.integratedOp(re.sub(u"\\<.*?\\>", "",c.replace('\r', '').replace('\n', '').replace('\u3000', '')))
                        content = content + '<p>' + c + '</p>'
            except Exception as e:
                pass
            articleContentItem['title'] = title_
            articleContentItem['content'] = content
            yield articleContentItem
