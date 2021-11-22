"""
    这里爬取的是文章信息的列表
"""
import scrapy
from fake_useragent import UserAgent
from .. import items

class gppzSpider(scrapy.Spider):
    name = "peizitoutiaoSpider"
    allow_domains = "www.peizitoutiao.com"
    # 对应栏目名
    topicName = ['pztt', 'gppz', 'pzpt', 'pzgs']  # 爬取的对应栏目名 改动的位置
    map_Dict = {
        'pztt' : 'list-16-',
        'gppz' : 'list-1-',
        'pzpt' : 'list-3-',
        'pzgs' : 'list-4-',
    }
    map_Dict_Tag = {
        'pztt': '配资头条',
        'gppz': '股票配资',
        'pzpt': '配资平台',
        'pzgs': '配资公司',
    }
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': str(UserAgent().random),
    }
    def start_requests(self):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': str(UserAgent().random),
        }
        for topic in self.topicName:
            url = "https://www.peizitoutiao.com/" + topic
            yield scrapy.Request(url = url, callback=self.parse, headers=headers)

    # 获取每一页
    def parse(self, response, **kwargs):
        if('list' in response.url):
            curTopic = response.url.split('list')[0].split('/')[-2]
        else:
            curTopic = response.url.split('/')[-2]
        # 获取总页码
        num = int(response.xpath("//div[@class='gppzpt_my_pages']/ul/li/a/@href").extract()[-1].split('.')[0].split('-')[-1])
        # 下一页
        for i in range(1, num+1):
            if('list' in response.url):
                url_ = response.url.split('list')[0] + self.map_Dict[curTopic] + str(i) + ".html"
            else:
                url_ = response.url + self.map_Dict[curTopic] + str(i) + ".html"
            yield scrapy.Request(url=url_, callback=self.parse_info, headers=self.headers, dont_filter=True)

    # 获取每一页文章信息
    def parse_info(self, response):
        if ('list' in response.url):
            curTopic = response.url.split('list')[0].split('/')[-2]
        else:
            curTopic = response.url.split('/')[-2]
        # 获取文章信息列表
        articleInfoList = response.xpath("//div[@class='gppzpt_fc']/ul/li")
        articleInfoItem = items.ArticlesInfoItem()
        articleUrlList = []
        for article in articleInfoList:
            articleInfoItem['title'] = article.xpath(".//h2/text()").extract_first()
            articleInfoItem['author'] = "".join(
                article.xpath(".//div[@class='gppzpt_zx_author']/text()").extract()).replace(" ", "").replace("\n", "")
            articleInfoItem['publishTime'] = article.xpath(
                ".//div[@class='gppzpt_zx_author']/span/text()").extract_first()
            url = "https://www.peizitoutiao.com" + article.xpath(".//div[@class='gppzpt_zx_title pull-right']//a/@href").extract_first()
            articleInfoItem['url'] = url
            tag = article.xpath(".//div[@class='gppzpt_zx_tag']/a/text()").extract_first()
            if(not tag):
                tag = self.map_Dict_Tag[curTopic]
            articleInfoItem['tag'] = tag
            articleInfoItem['tableName'] = 'tb_articleinfo'
            articleUrlList.append((url, tag))
            yield articleInfoItem

        for articleUrl in articleUrlList:
            add_para = {}
            add_para['tagOri'] = articleUrl[1]
            yield scrapy.Request(url=articleUrl[0], callback=self.parse_Content, cb_kwargs=add_para, dont_filter=True)

    # 获取文章内容
    def parse_Content(self, response, tagOri):
        paragraphList = response.xpath("//div[@class='gppzpt_arc_neirong gppzpt_arc_neirong_new']/p").xpath(
            "string(.)").extract()
        '''
            1 这里要清除第一段落和最后一段落
            2 判断是否包含文章的标签词
        '''
        articlesContentItem = items.ArticlesContentItem()
        for i in range(1, len(paragraphList) - 1):
            if (paragraphList[i].replace("\r\n\t", "").replace("\xa0", "") != ""):
                articlesContentItem['url'] = response.url
                articlesContentItem['paragraph'] = paragraphList[i]
                # articlesContentItem['infoId'] = infoId
                if (tagOri in paragraphList[i]):
                    articlesContentItem['hasTag'] = 'True'
                else:
                    articlesContentItem['hasTag'] = 'False'
                articlesContentItem['tableName'] = 'tb_articlecontent'
                yield articlesContentItem
    def close(spider, reason):
        print("爬取结束")
