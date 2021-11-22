"""
    这里爬取的是文章的内容
"""
import scrapy, pymysql
from fake_useragent import UserAgent
from ..items import ArticlesContentItem

# 从数据库获取url
def getFromMysql(topicName):
    conn = pymysql.connect(
        host='localhost',
        user="root",
        passwd="root",
        db="peizitoutiaodatabase",
        autocommit=True
    )
    cursor = conn.cursor()
    sql = "SELECT `id`,`url`,`tag_origin` FROM peizitoutiaodatabase.tb_" + topicName + "_articleinfo;"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


class gppzSpider(scrapy.Spider):
    name = "ArticlesContentSpider"
    allow_domains = "www.peizitoutiao.com"
    # 对应栏目名
    topicName = 'pzpt'  # 爬取的对应栏目名
    start_urls = getFromMysql(topicName)
    # start_urls = [(1, 'www.peizitoutiao.com//gppz/2021/0810/10977.html','配资模式')]

    def start_requests(self):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': str(UserAgent().random),
        }
        add_params = {}
        for urlItem in self.start_urls:
            add_params['infoId'] = urlItem[0]
            add_params['tagOri'] = urlItem[2]
            yield scrapy.Request(url='http://'+urlItem[1], callback=self.parse_articleContent, headers=headers, cb_kwargs=add_params)


    # 获取文章信息列表
    def parse_articleContent(self, response, infoId, tagOri):
        paragraphList = response.xpath("//div[@class='gppzpt_arc_neirong gppzpt_arc_neirong_new']/p").xpath("string(.)").extract()
        '''
            1 这里要清除第一段落和最后一段落
            2 判断是否包含文章的标签词
        '''
        for i in range(1,len(paragraphList)-1):
            if(paragraphList[i].replace("\r\n\t","").replace("\xa0","")!=""):
                articlesContentItem = ArticlesContentItem()
                articlesContentItem['paragraph'] = paragraphList[i]
                articlesContentItem['infoId'] = infoId
                if(tagOri in paragraphList[i]):
                    articlesContentItem['hasTag'] = 'True'
                else:
                    articlesContentItem['hasTag'] = 'False'
                articlesContentItem['tableName'] = self.topicName
                yield articlesContentItem
