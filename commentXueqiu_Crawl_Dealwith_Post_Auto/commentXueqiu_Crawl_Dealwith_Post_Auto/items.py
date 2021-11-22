# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleInfoItem(scrapy.Item):
    url = scrapy.Field()
    publishTime = scrapy.Field()

class CommentItem(scrapy.Item):
    comment = scrapy.Field()
    fromUrl = scrapy.Field()
    publishTime = scrapy.Field()