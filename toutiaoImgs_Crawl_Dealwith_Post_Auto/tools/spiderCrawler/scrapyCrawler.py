from scrapy import cmdline

def excuteScrapyByOrder(args="Scrapy crawl toutiaoArticleInfoSpider"):
    args = args.split()
    cmdline.execute(args)
    pass