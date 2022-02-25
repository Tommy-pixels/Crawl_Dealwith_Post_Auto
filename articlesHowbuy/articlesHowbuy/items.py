import scrapy


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    content=scrapy.Field()
