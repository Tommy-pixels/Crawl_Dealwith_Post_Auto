# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ArticlesInfoItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    publishTime = scrapy.Field()
    url = scrapy.Field()
    tag = scrapy.Field()
    tableName = scrapy.Field()  # 数据库存放数据的表名

class ArticlesContentItem(scrapy.Item):
    url = scrapy.Field()
    paragraph = scrapy.Field()
    infoId = scrapy.Field()
    hasTag = scrapy.Field()
    tableName = scrapy.Field()  # 数据库存放数据的表名
