# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NameCodeItem(scrapy.Item):
    name = scrapy.Field()
    code = scrapy.Field()
    belong = scrapy.Field()
