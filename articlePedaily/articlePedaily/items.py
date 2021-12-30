import scrapy


class ArticleContentItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()