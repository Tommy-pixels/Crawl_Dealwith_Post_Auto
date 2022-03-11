import scrapy, time
from fake_useragent import UserAgent
from .. import items
from auto_datahandler.customFunction__.Cleaner.cleaner_paragraph import Cleaner_Paragraph
from auto_datahandler.basement__.IsCheck import IsCheck_uchar
from auto_datahandler.basement__.ContralerDatabase import Contraler_Database
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
        'Host': 'blog.csdn.net',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    cookies = {
    }
    db = Contraler_Database('dbfreeh')
    UPDATE_NOTE = "UPDATE `tb_article` SET `note` = '{}' WHERE (`id` = '{}');"

    def start_requests(self):
        sql_origin = 'SELECT `id`,`ori_url`,`title` FROM `dbfreeh`.`tb_article`;'
        sql_ = "SELECT `id`,`ori_url`,`title` FROM `dbfreeh`.`tb_article` WHERE `content`='' AND `note` is Null and `id`<1000;"
        self.db.cursor.execute(sql_)
        article_lis = self.db.cursor.fetchall()
        # article_lis = article_lis[0:999]
        for article in article_lis:
            id_a = article[0]
            url = article[1]
            title = article[2]
            if('download.csdn.net' in url):
                # 打标签
                self.db.cursor.execute(self.UPDATE_NOTE.format('下载页面', id_a))
                continue
            self.headers['User-Agent'] = str(UserAgent().random)
            dic = {}
            dic['id_a'] = id_a
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse_content, cb_kwargs=dic)
            time.sleep(5)

    def parse_content(self, response, id_a):
        articleContentItem = items.ArticleContentItem()
        pList = response.xpath('//div[@class="blog-content-box"]/article/div[@id="article_content"]/div[@id="content_views"]/*')
        if(len(pList)==1):
            pList = response.xpath('//div[@class="blog-content-box"]/article/div[@id="article_content"]/div[@id="content_views"]/*')[0].xpath('./*')

        content = ''
        cleaner_paragraph = Cleaner_Paragraph()
        # 判断文章是否vip文章或是专栏文章
        try:
            vip_mask = response.xpath('//div[@class="vip-mask"]')
            if(vip_mask):
                self.db.cursor.execute(self.UPDATE_NOTE.format('VIP文章', id_a))
                print(id_a, ' 是vip文章')
        except Exception as e:
            print(id_a, ' 非vip文章')

        try:
            zhuanlan_mask = response.xpath('//div[@class="column-mask"]')
            if(zhuanlan_mask):
                self.db.cursor.execute(self.UPDATE_NOTE.format('专栏文章', id_a))
                print(id_a, ' 是需要订阅的专栏文章')
        except Exception as e:
            print(id_a, ' 非专栏文章')

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
        if(len(pList)>15):
            for i in pList[-3:]:
                c = i.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','')
                if(len(c)!=0 and _str_check(c)):
                    pList.pop(pList.index(i))

        # 4 内容提取
        for p in pList:
            c = p.xpath('string(.)').extract_first().replace('\u3000', '').replace(' ','').replace('　', '').replace('\xa0','').replace('\r','').replace('\n','').replace('\t','')
            # 指定内容才筛选链接
            if(0<len(c)<80 and _str_check(c)):
                continue
            if ('版权说明' in c or '下面二维码' in c or '可关注微信公众号' in c or '微信公众号' in c or '邮箱地址' in c or '请关注公众号' in c or '相关系列：' in c
                or 'END' in c or '推荐阅读：' in c or '加微信' in c or '扫码下面二维码' in c ):
                break
            # 4.1 需要跳过的
            lis_continue = ['本分享为', 'QQ交流群', '更多分享', '作者：', '来源：', '原文：', '版权声明：', '文章出自', '公众号：', '抖音号：', '版权声明：','原文链接：']
            check = False
            for i_continue in lis_continue:
                if(i_continue in c):
                    check = True
                    break
            if(check):
                continue

            if(c != '' and p.extract().startswith('<pre')):
                content = content + "<code>" + p.xpath('string(.)').extract_first() + "</code>"
            elif(c != '' and p.extract().startswith('<table')):
                table = p.xpath('./tbody').extract()
                if(type(table)==list):
                    table = table[0]
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
        articleContentItem['id_a'] = id_a
        articleContentItem['content'] = content
        yield articleContentItem

