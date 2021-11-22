# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    title = scrapy.Field()
    videoUrl = scrapy.Field()
    publishTime = scrapy.Field()
    duration = scrapy.Field()