import scrapy
from .. import items

class magicSunshading(scrapy.Spider):
    name = "magicSunshadingSpider"
    allowed_domains = 'www.magic-sunshading.com'
    '''
        'https://www.magic-sunshading.com/pzgs/',
        'https://www.magic-sunshading.com/wlpz/',
        'https://www.magic-sunshading.com/cgpz/',
    '''
    start_urls = [
        'https://www.magic-sunshading.com/pzgs/',
        'https://www.magic-sunshading.com/wlpz/',
        'https://www.magic-sunshading.com/cgpz/',
        'https://www.magic-sunshading.com/pzfw/',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse
            )

    def parse(self, response):
        articleInfoItem = items.ArticlesInfoItem()
        urlList = []
        # print(response.url)
        if(len(response.url.replace("https://www.magic-sunshading.com/","")) == 5):
            # 处理文章信息列表
            liList = response.xpath("//div[@class='article-list list-show']/ul/li")

            for li in liList:
                title = li.xpath(".//h2/a/text()").extract_first()
                url = response.url + "/".join(li.xpath(".//h2/a/@href").extract_first().split('/')[2:])
                tag = li.xpath(".//div[@class='right-bottom']/a/text()").extract_first()
                publishTime = li.xpath(".//div[@class='right-time']/text()").extract_first()
                articleInfoItem["title"] = title
                articleInfoItem["url"] = url
                articleInfoItem["tag"] = tag
                articleInfoItem["publishTime"] = publishTime
                articleInfoItem["tableName"] = 'tb_keyparagraph_magicsunshading_articleinfo'
                urlList.append((url,tag))
                yield articleInfoItem
        for urlItem in urlList:
            add_params = {}
            add_params['tagOri'] = urlItem[1]
            yield scrapy.Request(url=urlItem[0], callback=self.parse_article, dont_filter=True, cb_kwargs=add_params)


    def parse_article(self, response, tagOri):
        articleContentItem = items.ArticlesContentItem()
        # print("parse_article runing")
        # print(response.url)
        paragraphList = response.xpath("//div[@class='article-content']/p").xpath("string(.)").extract()
        for i in range(1, len(paragraphList) - 1):
            if (paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                articleContentItem['url'] = response.url
                articleContentItem['paragraph'] = paragraphList[i]
                if (tagOri in paragraphList[i]):
                    articleContentItem['hasTag'] = 'True'
                else:
                    articleContentItem['hasTag'] = 'False'
                articleContentItem["tableName"] = 'tb_keyparagraph_magicsunshading_articlecontent'
                yield articleContentItem
