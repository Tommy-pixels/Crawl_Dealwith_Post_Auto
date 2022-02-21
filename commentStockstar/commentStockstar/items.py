import scrapy


class CommentItem(scrapy.Item):
    comment = scrapy.Field()
    publishTime = scrapy.Field()
