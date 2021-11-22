# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class articleInfoItem(scrapy.Item):
    dateline = scrapy.Field()
    formatDate = scrapy.Field()
    origin_pic_path = scrapy.Field()    # 存放原图路径
    pic_path = scrapy.Field()
    title = scrapy.Field()
    user_name = scrapy.Field()
    user_uid = scrapy.Field()
    user_avatar = scrapy.Field()
    databaseTbName = scrapy.Field()


