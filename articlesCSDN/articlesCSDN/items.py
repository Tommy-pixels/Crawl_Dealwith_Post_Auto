import scrapy

class ArticleItem(scrapy.Item):
    article_id = scrapy.Field()
    title = scrapy.Field()
    create_time = scrapy.Field()
    author = scrapy.Field()
    url = scrapy.Field()
    crawl_time = scrapy.Field()

class ArticleContentItem(scrapy.Item):
    content = scrapy.Field()



