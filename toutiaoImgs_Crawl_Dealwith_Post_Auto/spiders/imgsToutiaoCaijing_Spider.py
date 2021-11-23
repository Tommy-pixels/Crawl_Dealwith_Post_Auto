import scrapy, pymysql
import items
import json, time, random
from fake_useragent import UserAgent

from tools import basic

# 从数据库中获取需要下载图片的文章的链接 注意做好去重
def getArticleUrlFromMysql():
    urlList = []
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="imgsdatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    sql = "SELECT * FROM `imgsdatabase`.`tb_toutiao_test`;"
    cursor.execute(sql)
    result = cursor.fetchall()
    for item in result:
        if(item[2]!='' and item[2]!='无链接'):
            if(item[2] not in urlList):
                urlList.append(item[2])
        elif(item[3]!='' and item[3]!='无链接'):
            if(item[3] not in urlList):
                urlList.append(item[3])
        else:
            pass
    cursor.close()
    conn.close()
    return urlList

class toutiaoSpider(scrapy.Spider):
    name = "toutiaoImgsSpider"
    # allowed_domains = ["www.toutiao.com"]
    # ----------------------- 手动获取cookies和signature的方式 -----------------------------------
    # signature = "_02B4Z6wo00901FMEwGAAAIDD4.Usq.xcyVhTIMTAAHXhTDiZQ.Lfoqz2vzJaGXIn0fkszB8KU1he77sxAbacVLOoGXS0Q94gYb7-6oJg4dGrHH9hiVDTPgHl2HOlXiEdT2gCoOJK8GBXyktV7e"
    # cleaner = basic.cleanCookiesAndHeadersByRow()
    # cookies = cleaner.translateCookies("tt_webid=6997201632312428062; ttcid=dd3cce38181540aaa103d89ef6c14bbb18; s_v_web_id=verify_ksfhhwhb_Z8NKNkAU_phg4_4i3s_ABsm_a3BdovT1CeA2; csrftoken=09761f8fcba3e866f1a0dad6165b9ca2; MONITOR_WEB_ID=6997201632312428062; ttwid=1%7CXBar468_F1dQc0Ocwu8swRlVQjeYIPhnzvqeLLAKs0g%7C1629169577%7C6635f4eebcce43ad37c6cbd6b1e43157249ccfbc528fa94274e10896133bcd69; tt_scid=VcxE8mBlvClnehEXx7YxmRs0beEY-0gjTnSbU4foIYIrZXwrQOc.pnOWAW.L-RJ8d0c0")
    # ------------------------- 自动获取cookies和signature的方式
    # toutiao = basic.articleUrl_toutiao()
    # toutiaocookiesAndSignature = toutiao.get_cookiesAndSignature()
    # cookies = toutiaocookiesAndSignature["cookies"]
    # signature = toutiaocookiesAndSignature["signature"]

    start_urls = getArticleUrlFromMysql()
    # start_urls = 'https://www.toutiao.com/a6971793525323137543/?log_from=1856c80c1bd23_1629792220292'
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': str(UserAgent().random),
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.toutiao.com/'
        }
    # 'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',

    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="imgsdatabase",
        autocommit=True
    )
    cursor = conn.cursor()

    def start_requests(self):
        for item in self.start_urls:
            sleeptime = random.randint(0, 5)
            # 每次请求前都要通过模拟浏览器获取cookie和signature 随机时间
            time.sleep(sleeptime)
            toutiao = basic.articleUrl_toutiao()
            toutiaocookiesAndSignature = toutiao.get_cookiesAndSignature()
            toutiaoCookies = toutiaocookiesAndSignature["cookies"]
            self.signature = toutiaocookiesAndSignature["signature"]

            toutiaoCookies['User-Agent'] = str(UserAgent().random)
            yield scrapy.Request(item, callback=self.parse_article, cookies=toutiaoCookies, headers=self.headers, dont_filter=False)

    # 随机时间
    def randomSleep(self):
        sleepTime = random.randint(0,15)
        time.sleep(sleepTime)
        pass


    # 获取新cookie
    def getNewCookie(self):
        toutiao = basic.articleUrl_toutiao()
        toutiaocookiesAndSignature = toutiao.get_cookiesAndSignature()
        return toutiaocookiesAndSignature["cookies"]

    def getNewHeader(self):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': str(UserAgent().random),
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.toutiao.com/'
        }
        return headers

    def parse_article(self, response, **kwargs):
        if(response.status==200):
            # 获取图片链接并保存
            imgUrlList = response.xpath("//article//img/@src").extract()
            if(imgUrlList):
                print("处理的urlList如下：")
                print(imgUrlList)
                for url in imgUrlList:
                    sql = "INSERT INTO `imgsdatabase`.`tb_toutiao_test` (`imgUrl`, `originUrl`) VALUES (\'{}\', \'{}\');".format(url, response.url)
                    result = self.cursor.execute(sql)
                    if (result == 1):
                        print("插入图片url成功:  ", url)
                        pass
                    else:
                        print("插入记录失败： ", sql)
                    toutiaoImg = items.toutiaoImgItem()
                    toutiaoImg["imgUrl"] = url
                    # 从数据库获取id 用于下载图片的时候命名
                    sqlGetId = "Select `id` From `imgsdatabase`.`tb_toutiao_test` where `imgUrl` = \'{}\'".format(url)
                    self.cursor.execute(sqlGetId)
                    id = self.cursor.fetchone()
                    toutiaoImg["imgName"] = id[0]
                    yield toutiaoImg
            else:
                sql = "INSERT INTO `imgsdatabase`.`tb_toutiao_test` (`imgUrl`, `originUrl`) VALUES (\'{}\', \'{}\');".format(
                    '该链接找不到图片', response.url)
                self.cursor.execute(sql)
        else:
            sql = "INSERT INTO `imgsdatabase`.`tb_toutiao_test` (`imgUrl`, `originUrl`) VALUES (\'{}\', \'{}\');".format(
                str(response.status), response.url)
            self.cursor.execute(sql)
            print("---------------------------------------------------------------------")
