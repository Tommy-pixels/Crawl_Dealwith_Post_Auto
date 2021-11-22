import scrapy, json
from .. import items
from fake_useragent import UserAgent

'''
    Cookie: 
'''
class ZhidxSpider(scrapy.Spider):
    name = 'zhidxSpider'
    start_url = 'https://zhidx.com/wp-admin/admin-ajax.php'
    headerStr = '''
        Host: zhidx.com
        Connection: keep-alive
        sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
        Accept: */*
        X-Requested-With: XMLHttpRequest
        sec-ch-ua-mobile: ?0
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
        Content-Type: application/x-www-form-urlencoded; charset=UTF-8
        Origin: https://zhidx.com
        Sec-Fetch-Site: same-origin
        Sec-Fetch-Mode: cors
        Sec-Fetch-Dest: empty
        Referer: https://zhidx.com/
        Accept-Encoding: gzip, deflate, br
        Accept-Language: zh-CN,zh;q=0.9
    '''
    cookieStr = 'PHPSESSID=2240f8eb2dfd59996b651b3ac8c3a5ea; Hm_lvt_6a105aad5d4cd3c47e5745e226ca9ccc=1635816786,1635817477,1635821556; Hm_lpvt_6a105aad5d4cd3c47e5745e226ca9ccc=1635821556'
    webForm = 'action=category_list&page={}'

    def start_requests(self):
        headerList = self.headerStr.split('\n')
        self.header = {}
        for headerItem in headerList:
            i = headerItem.strip().split(": ")
            if (i != ['']):
                k = i[0]
                v = i[1]
                self.header[k] = v
        cookieList = self.cookieStr.split(";")
        self.cookie = {}
        for cookieItem in cookieList:
            i = cookieItem.strip().split("=")
            k = i[0]
            v = i[1]
            self.cookie[k] = v
        for i in range(1015):
            self.header['User-Agent'] = str(UserAgent().random)
            webForm = self.webForm.format(str(i))
            yield scrapy.Request(url=self.start_url, cookies=self.cookie, headers=self.header, callback=self.parse_aritcle, method='POST', body=webForm)

    def parse_aritcle(self, response):
        dataList = json.loads(response.text)['result']
        imgItem = items.ImgItem()
        for data in dataList:
            fromUrl = str(response.request.body, encoding='utf-8')
            if('src=' in data['mb_pic']):
                if('https' not in data['mb_pic']):
                    imgSrc = 'https:' + str(data['mb_pic'].split('src=')[-1].split('class')[0]).split('"')[1]
                else:
                    imgSrc = str(data['mb_pic'].split('src=')[-1].split('class')[0]).split('"')[1]
            elif('src =' in data['mb_pic']):
                if('https' not in data['mb_pic']):
                    imgSrc = 'https:' + str(data['mb_pic'].split('src =')[-1].split('class')[0]).split('"')[1]
                else:
                    imgSrc = str(data['mb_pic'].split('src =')[-1].split('class')[0]).split('"')[1]
            else:
                print("fromUrl: ", fromUrl, " datapic: ", data['mb_pic'])
                continue

            if('?' in imgSrc):
                imgSrc = imgSrc.split('?')[0]
            imgItem['imgUrl'] = imgSrc
            imgItem['from_url'] = fromUrl
            yield imgItem
