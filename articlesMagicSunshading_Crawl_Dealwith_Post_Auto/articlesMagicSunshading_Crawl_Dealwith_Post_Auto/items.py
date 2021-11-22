# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticlesInfoItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    tag = scrapy.Field()
    publishTime = scrapy.Field()
    tableName = scrapy.Field()

class ArticlesContentItem(scrapy.Item):
    url = scrapy.Field()
    paragraph = scrapy.Field()
    hasTag = scrapy.Field()
    tableName = scrapy.Field()
