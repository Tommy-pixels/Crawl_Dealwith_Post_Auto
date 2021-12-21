import scrapy

class QuestionItem(scrapy.Item):
    tag = scrapy.Field()
    question = scrapy.Field()
    page_url = scrapy.Field()
    question_url = scrapy.Field()

class AnswerItem(scrapy.Item):
    question_id = scrapy.Field()
    answer = scrapy.Field()
    totle_answer = scrapy.Field()
