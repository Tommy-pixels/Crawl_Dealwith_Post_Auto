import scrapy
from .. import items

class blogcmsSpider(scrapy.Spider):
    name = 'BlogcmsSpider'
    start_urls = [
        'https://www.blogcms.cn/pzkh',
        'https://www.blogcms.cn/zxpz',
        'https://www.blogcms.cn/cgpz',
        'https://www.blogcms.cn/pzpt',
        'https://www.blogcms.cn/zqpz'
    ]
    # allow_domains = []

    # blogcms网站对应 - 后加数字表示第几页第几页
    mapDict = {
        'pzkh': 'list-1-',
        'zxpz': 'list-2-',
        'cgpz': 'list-3-',
        'pzpt': 'list-4-',
        'zqpz': 'list-5-'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 文章基础列表
    def parse(self, response, **kwargs):
        # 对文章列表信息的处理
        urlList = []
        urlKind = response.url.split('/')[-2]
        urlPart = self.mapDict[urlKind]
        num = response.xpath("//div[@class='page-box']/ul/li/a/@href")[-1].extract().split('.')[0].split('-')[-1]
        # 本页的文章信息列表
        articleList = response.xpath("//div[@class='chapter-num chapter-show']/ul/li")
        articleInfoItem = items.ArticleInfoItem()
        articleUrlList = []
        for article in articleList:
            articleInfoItem['title'] = article.xpath(".//h2/a").xpath("string()").extract_first()
            if('list' in response.url):
                head = response.url.split("/")[0:-1][0] + "//" + response.url.split("/")[0:-1][2] + "/" + response.url.split("/")[0:-1][3] + '/'
                url = head + article.xpath(".//h2/a/@href").extract_first().replace('/' + urlKind + '/', "")
            else:
                url = response.url + article.xpath(".//h2/a/@href").extract_first().replace('/' + urlKind + '/', "")
            articleInfoItem['url'] = url
            try:
                tag = article.xpath(".//div[@class='clearfix address']/a[@class='biao qian label']/text()").extract_first()
            except Exception as e:
                tag = '无Tag'
            articleInfoItem['tag'] = tag
            articleInfoItem['publishTime'] = article.xpath(".//div[@class='clearfix address']/span[@class='time']/text()").extract_first()
            articleInfoItem['tableName'] = 'tb_keyparagraph_blogcms_articleinfo'
            articleUrlList.append((url, tag))
            yield articleInfoItem
        for urlItem in articleUrlList:
            add_para = {}
            add_para['tagOri'] = urlItem[1]
            yield scrapy.Request(url=urlItem[0], callback=self.parse_content, dont_filter=True, cb_kwargs=add_para)


        # 下一页的链接
        for i in range(2, int(num)+1):
            urlList.append(response.url + urlPart + str(i) + '.html')
            yield scrapy.Request(url=response.url + urlPart + str(i) + '.html', callback=self.parse, dont_filter=True)

    def parse_content(self, response, tagOri):
        # 对文章内容进行处理
        paragraphList = response.xpath("//div[@class='article-content']/p").xpath("string(.)").extract()
        contentItem = items.ArticleContentItem()
        for i in range(1, len(paragraphList) - 1):
            if (paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                contentItem['url'] = response.url
                contentItem['paragraph'] = paragraphList[i]
                if (tagOri and tagOri in paragraphList[i]):
                    contentItem['hasTag'] = 'True'
                else:
                    contentItem['hasTag'] = 'False'
                contentItem['tableName'] = 'tb_keyparagraph_blogcms_articlecontent'
                yield contentItem

    def close(spider, reason):
        print("爬取结束")
