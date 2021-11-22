import scrapy

# 头条 文章信息
class toutiaoArticleInfoItem(scrapy.Item):
    title = scrapy.Field()
    article_url = scrapy.Field()
    share_url = scrapy.Field()
    behot_time = scrapy.Field()
    group_id = scrapy.Field()
    has_image = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    user_avatarUrl = scrapy.Field()

# 头条 图片链接
class toutiaoImgItem(scrapy.Item):
    imgUrl = scrapy.Field()
    imgName = scrapy.Field()

