# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class articleInfoItem(scrapy.Item):
    # 单篇文章信息
    url = scrapy.Field()
    title = scrapy.Field()
    publishTime = scrapy.Field()
    kind = scrapy.Field()

class articleContentItem(scrapy.Item):
    url = scrapy.Field()
    paragraph = scrapy.Field()
