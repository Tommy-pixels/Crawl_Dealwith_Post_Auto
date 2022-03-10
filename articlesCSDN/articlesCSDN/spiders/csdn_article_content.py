import scrapy, time
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.basement__.IsCheck import IsCheck_uchar
import re

"""CSDN 文章内容过滤规则
    过滤uri
"""
def del_btw(s, l, r):
    r_rule = l + u".*?" + r
    res = re.sub(r_rule, "", s)
    return res

def _str_check(s):
    alpha_num = 0
    def is_b(d):
        lis = ['.','/',':','_','?','&', '|']
        if(d in lis):
            return True
        else:
            return False
    for c in s:
        if(IsCheck_uchar.is_alphabet(c) or is_b(c) or IsCheck_uchar.is_number(c)):
            alpha_num = alpha_num + 1
    ratio = alpha_num/len(s)
    if(ratio>0.80):
        return True
    else:
        return False

class CSDNSpider(scrapy.Spider):
    name = 'csdnarticleSpider'

    start_url = 'https://blog.csdn.net/qq_19782019/article/details/80259836?ops_request_misc=&request_id=&biz_id=102&utm_term=%E6%8E%A5%E5%8F%A3&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-0-80259836.nonecase&spm=1018.2226.3001.4449'
    headers = {
        'Host': 'gsp0.baidu.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'script',
        'Referer': 'https://so.csdn.net/so/search?q=%E6%8E%A5%E5%8F%A3&t=all&u=&s=0&lv=5&tm=0',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
        'BAIDUID_BFESS':'D458AC18B8D6743CBCF03D93C5C57D02:FG=1'
    }
    def start_requests(self):
        article_lis = []
        for url in article_lis:
            if('download.csdn.net' in url):
                continue
            self.headers['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content)
            time.sleep(5)

    def parse_content(self, response):
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath('//div[@class="blog-content-box"]/article/div[@id="article_content"]/div[@id="content_views"]/*')
        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        # 1 清除文章目录
        for i in pList[0:4]:
            if(i.extract().startswith('<div class="toc">')):
                pList.pop(pList.index(i))
                break
        # 2 清除头图片
        for i in pList[0:2]:
            if(i.xpath('.//img') != []):
                pList.pop(pList.index(i))
                break
        # 3 处理清除文章模块潜在的链接部分 如 整一段为 https:XXX.XXX.XX 没有中文的这种情况 以及 超链接文字的内容
        for i in pList[-5:]:
            c = i.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','')
            if(_str_check(c)):
                pList.pop(pList.index(i))


        # 4 内容提取
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','')
            # 指定内容才筛选链接
            if(len(c)<80 and _str_check(c)):
                continue
            if ('版权说明' in c or '下面二维码' in c or '可关注微信公众号' in c or '微信公众号' in c or '邮箱地址' in c or '请关注公众号' in c or '相关系列：' in c
                or 'END' in c or '推荐阅读：' in c or '加微信' in c or '扫码下面二维码' in c ):
                break
            if('本分享为' in c or 'QQ交流群' in c or '更多分享'in c or '作者：' in c or '来源：' in c or '原文：' in c or '版权声明：' in c or ''):
                continue
            if(c != '' and p.extract().startswith('<pre')):
                content = content + "<code>" + p.xpath('string(.)').extract_first() + "</code>"
            elif(c != '' and p.extract().startswith('<table')):
                table = p.xpath('./tbody').extract()
                c = del_btw(table,' style="','"')
                c = del_btw(c, ' rowspan="', '"')
                content = content + "<table>" + c + '</table>'
            elif(c != ''):
                c = cleaner_paragraph.integratedOp(c)
                # if(int(len(c))<3):
                #     pass
                # else:
                content = content + '<p>' + c + '</p>'
            if(p.xpath('.//img') != []):
                for img in p.xpath(".//img"):
                    content = content + "<img src='" + img.xpath('./@src').extract_first() + "' />"

        articleContentItem['title'] = ''
        articleContentItem['content'] = content
        yield articleContentItem

