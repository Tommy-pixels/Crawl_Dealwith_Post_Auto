import scrapy


class ArticleItem(scrapy.Item):
    publishTime = scrapy.Field()
    url = scrapy.Field()

class ArticleContentItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
