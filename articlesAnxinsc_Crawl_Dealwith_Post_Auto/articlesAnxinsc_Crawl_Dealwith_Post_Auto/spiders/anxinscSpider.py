import scrapy
from .. import items

class anxinscSpider(scrapy.Spider):
    name = "anxinscSpider"
    start_urls = [
        'https://www.anxinsc.com/pzyys',
        'https://www.anxinsc.com/pzcg/',
        'https://www.anxinsc.com/pzpt/',
        'https://www.anxinsc.com/zxpz/',
        'https://www.anxinsc.com/pzfw/'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_Info)

    def parse_Info(self, response, **kwargs):
        # 获取文章列表
        articleList = response.xpath("//div[@class='article-list list-show']/ul/li")
        articleInfoItem = items.ArticleInfoItem()
        urlKind = response.url.split('/')[-2]
        articleUrlList = []
        for article in articleList:
            articleInfoItem['title'] = article.xpath(".//h2/a").xpath("string(.)").extract_first()
            url = response.url + article.xpath(".//h2/a/@href").extract_first().replace('/' + urlKind + '/', "")
            articleInfoItem['url'] = url
            tag = article.xpath(".//div[@class='right-bottom']/a/text()").extract_first()
            articleInfoItem['tag'] = tag
            articleInfoItem['publishTime'] = article.xpath(".//div[@class='list-right']//div[@class='time-img ']/text()").extract_first()
            articleInfoItem['tableName'] = 'tb_keyparagraph_anxinsc_articleinfo'
            articleUrlList.append((url, tag))
            yield articleInfoItem

        for urlItem in articleUrlList:
            add_para = {}
            add_para['tagOri'] = urlItem[1]
            yield scrapy.Request(url=urlItem[0], callback=self.parse_content, cb_kwargs=add_para, dont_filter=True)


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
                contentItem['tableName'] = 'tb_keyparagraph_anxinsc_articlecontent'
                yield contentItem
