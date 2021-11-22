'''
    爬虫启动
        爬取 - 识别 - 处理 - post
'''
import pymysql

from tools import fundemental as fd
from tools import basic
from tools.imgClassifier import classifierBaiduApi
from tools.imgFilter import filter
import os, subprocess
from tools.spiderCrawler import scrapyCrawler
from tools.imgProcessing import imgProcess

# 将目录下的图片图片传到接口
# 配置
# 获取当前目录所在绝对路径
proj_absPath = os.path.abspath(os.path.dirname(__file__))
updateTime = basic.getCurDate()
oriDomain = 'huxiu'
setting = {
    # 爬取下来的图片的存放路径
    'imgsCrawledDir' : proj_absPath + '\\assets\imgsCrawled\\' + updateTime + '\\' + oriDomain + '\\',
    # 经过百度识别重命名后存放的目录路径
    'imgsReconizedDir': proj_absPath + '\\assets\imgsReconized\\' + updateTime + '\\' + oriDomain + '\\',
    # 初步处理过后的无水印的图片的目录
    'imgsDirDontHasWaterMask' : proj_absPath + '\\assets\imgsDontHasWaterMask\\' + updateTime + '\\' + oriDomain + '\\',
    # 初步处理过后有水印的图片的目录
    'imgsDirHasWaterMask' : proj_absPath + '\\assets\imgDirHasWaterMask\\' + updateTime + '\\' + oriDomain + '\\',
    # 处理完成的图片目录
    'imgsCleanedDir' : proj_absPath + '\\assets\imgsCleanedDir\\' + updateTime + '\\' + oriDomain + '\\',
    # 缩略图保存位置图片目录
    'imgsThumbnailDir' : proj_absPath + '\\assets\imgsThumbnailDir\\' + updateTime + '\\' + oriDomain + '\\',
}

# 判断配置里的目录是否存在，不存在则创建对应目录
for item in setting.values():
    basic.checkACreateDir(item)

# 1 定时爬虫
# 1.1 爬取文章信息 保存在数据库 `huxiudatabase`.`tb_`;
i = 1
while(True):
    basic.randomSleep()
    # scrapyCrawler.excuteScrapyByOrder(args="Scrapy crawl huxiuArticleSpider")
    subprocess.Popen("Scrapy crawl toutiaoArticleInfoSpider")
    print("第 " + str(i) + " 次文章信息数据爬取")
    i = i + 1

# 从数据库获取图片链接 下载图片
# conn = pymysql.connect(
#         host='localhost',
#         user="root",
#         passwd="root",
#         db="huxiudatabase",
#         autocommit=True
# )

# cursor = conn.cursor()
# tableList = [
#     "tb_articleshuxiucaijing", "tb_articleshuxiucheyuchuxing" , "tb_articleshuxiuchuangyeweijian", "tb_articleshuxiuchuhai", "tb_articleshuxiujinrongdichang",
#     "tb_articleshuxiunianqingyidai", "tb_articleshuxiuqianyankeji", "tb_articleshuxiuqiyefuwu", "tb_articleshuxiuquanqiuredian",
#     "tb_articleshuxiushejiaotongxun", "tb_articleshuxiushenghuoqiangdiao", "tb_articleshuxiushiyixiaofeizhe", "tb_articleshuxiuwenhuajiaoyu",
#     "tb_articleshuxiuyiliaojiankang", "tb_articleshuxiuyuletaojin"
# ]
#
# for table in tableList:
#     sql = "SELECT `id`,`origin_pic_path` FROM `" + table + "`;"
#     cursor.execute(sql)
#     imgUrlPathList = cursor.fetchall()
#     for imgUrl in imgUrlPathList:
#         imgName = table + "_" + table.replace("tb_articleshuxiu","") + "_" + str(imgUrl[0])
#         basic.downimg(urlpath=imgUrl[1], imgname=imgName, dstDirPath=setting["imgsCrawledDir"])
# cursor.close()
# conn.close()

# 对爬取下来的图片进行处理 - 识别重命名、过滤、水印的识别及裁切 处理完后放在路径  ./assets/imgsCleanedDir 下
# 2 重命名
# classifier = classifierBaiduApi.imgsClassifier(crawledDirPath=setting['imgsCrawledDir'], savedDirPath=setting['imgsReconizedDir'])
# classifier.run()

# 3 过滤 (关键词过滤、空文件过滤、水印识别及处理）
# filter = filter.imgsFilter(
#     imgsDontHasWaterMaskDir=setting['imgsDirDontHasWaterMask'],
#     imgDirHasWaterMask=setting['imgsDirHasWaterMask'],
#     imgCleanedStep1 = setting['imgsCleanedDir'],
#     dirOriPath=setting['imgsReconizedDir']
# )
# filter.run()    # 这里再做一下优化

# 4 将过滤后的图片整成缩略图
# thumbnailOriDir = setting['imgsCleanedDir']
# thumbnailDstDir = setting['imgsThumbnailDir']
# imgprocesser = imgProcess.Imgs2ThumbnailByDir(thumbnailOriDirPath=thumbnailOriDir, thumbnailDstDirPath=thumbnailDstDir)
# imgprocesser.cutOff2ThumbnailByDir()


# # 4 创建图片发送的poster 传送处理完成的图片图片
# imgposter0 = fd.ImgPoster(imgDirPath=setting['imgsCleanedDir'])
# imgposter0.updateImgs()
imgposter0 = fd.ImgPoster(imgDirPath=setting['imgsThumbnailDir'])
imgposter0.updateImgsThumbnail()

