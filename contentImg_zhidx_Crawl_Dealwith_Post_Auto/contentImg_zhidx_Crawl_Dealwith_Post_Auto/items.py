# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ImgItem(scrapy.Item):
    imgUrl = scrapy.Field()
    from_url = scrapy.Field()
