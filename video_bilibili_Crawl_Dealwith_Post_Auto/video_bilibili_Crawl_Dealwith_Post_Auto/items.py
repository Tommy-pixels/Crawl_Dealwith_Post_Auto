# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class videoInfoItem(scrapy.Item):
    title = scrapy.Field()
    pubdate = scrapy.Field()
    bilibiliUrl = scrapy.Field()
    avValue = scrapy.Field()
    cid = scrapy.Field()
    videoUrl = scrapy.Field()
    duration = scrapy.Field()