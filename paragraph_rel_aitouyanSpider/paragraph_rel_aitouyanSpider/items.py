# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParagraphItem(scrapy.Item):
    paragraph = scrapy.Field()
    referArticleUrl = scrapy.Field()