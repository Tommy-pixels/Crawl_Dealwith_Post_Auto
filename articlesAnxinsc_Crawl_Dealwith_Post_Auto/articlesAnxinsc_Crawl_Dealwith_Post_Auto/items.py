
import scrapy

class ArticleContentItem(scrapy.Item):
    paragraph = scrapy.Field()
    tag_ori = scrapy.Field()