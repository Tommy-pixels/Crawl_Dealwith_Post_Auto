
import scrapy


class ArticleInfoItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    publishTime = scrapy.Field()
    kind = scrapy.Field()

class ArticleContentItem(scrapy.Item):
    url = scrapy.Field()
    paragraph = scrapy.Field()