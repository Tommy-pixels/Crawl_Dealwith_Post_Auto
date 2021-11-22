import scrapy
from .. import items

class shmeishidaSpider(scrapy.Spider):
    name = 'shmeishidaSpider'
    start_urls = [
        'https://www.shmeishida.com/pzmh/',
        'https://www.shmeishida.com/pzkh/',
        'https://www.shmeishida.com/pzpt/',
        'https://www.shmeishida.com/pzgs/',
        'https://www.shmeishida.com/pzcg/'
    ]
    # allow_domains = []
    map_Dict = {
        'pzmh': '配资门户',
        'pzkh': '配资开户',
        'pzpt': '配资平台',
        'pzgs': '配资公司',
        'pzcg': '配资炒股'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 文章基础列表
    def parse(self, response, **kwargs):
        print(response.url)
        # 对文章列表信息的处理
        urlKind = response.url.split('/')[-2]
        # 本页的文章信息列表
        articleList = response.xpath("//div[@class='chapter-num chapter-show']/ul/li")
        articleInfoItem = items.ArticleInfoItem()
        articleUrlList = []
        for article in articleList:
            articleInfoItem['title'] = article.xpath(".//h2/a").xpath("string()").extract_first()
            url = response.url + article.xpath(".//h2/a/@href").extract_first().replace('/' + urlKind + '/', "")
            articleInfoItem['url'] = url
            tag = article.xpath(".//div[@class='clearfix address']/a[@class='biao qian label']/text()").extract_first()
            if(not tag):
                articleInfoItem['tag'] = self.map_Dict[urlKind]
            else:
                articleInfoItem['tag'] = tag
            articleInfoItem['publishTime'] = article.xpath(".//div[@class='clearfix address']/span[@class='time']/text()").extract_first()
            articleInfoItem['dbName'] = 'paragraphdatabase'
            articleInfoItem['tableName'] = 'tb_keyparagraph_shmeishi_articleinfo'
            articleUrlList.append((url, articleInfoItem['tag']))
            yield articleInfoItem

        for urlItem in articleUrlList:
            add_para = {}
            add_para['tagOri'] = urlItem[1]
            yield scrapy.Request(url=urlItem[0], callback=self.parse_content, dont_filter=True, cb_kwargs=add_para)

    def parse_content(self, response, tagOri):
        # 对文章内容进行处理
        paragraphList = response.xpath("//div[@class='article-content']/p").xpath("string(.)").extract()
        contentItem = items.ArticleContentItem()
        for i in range(1, len(paragraphList) - 1):
            if (paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                contentItem['url'] = response.url
                contentItem['paragraph'] = paragraphList[i]
                if (tagOri in paragraphList[i]):
                    contentItem['hasTag'] = 'True'
                else:
                    contentItem['hasTag'] = 'False'
                contentItem['dbName'] = 'paragraphdatabase'
                contentItem['tableName'] = 'tb_keyparagraph_shmeishi_articlecontent'
                yield contentItem

    def close(spider, reason):
        print("爬取结束")
