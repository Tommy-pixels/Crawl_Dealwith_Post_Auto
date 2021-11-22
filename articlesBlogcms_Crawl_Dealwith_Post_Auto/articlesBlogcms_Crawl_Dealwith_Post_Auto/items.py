
import scrapy


class ArticleInfoItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    tag = scrapy.Field()
    publishTime = scrapy.Field()
    tableName = scrapy.Field()


class ArticleContentItem(scrapy.Item):
    url = scrapy.Field()
    paragraph = scrapy.Field()
    hasTag = scrapy.Field()
    tableName = scrapy.Field()