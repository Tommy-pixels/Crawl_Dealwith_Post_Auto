import scrapy

class ParagraphItem(scrapy.Item):
    paragraph = scrapy.Field()
    tag_ori = scrapy.Field()
