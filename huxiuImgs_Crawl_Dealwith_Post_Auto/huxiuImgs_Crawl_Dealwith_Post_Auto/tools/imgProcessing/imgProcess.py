from PIL import Image
import os
'''
    将图片转换成缩略图
'''
# 注意这里目录路径的最后要加上 “//”
class Imgs2ThumbnailByDir():
    def __init__(self, thumbnailOriDirPath, thumbnailDstDirPath):
        self.thumbnailOriDirPath = thumbnailOriDirPath
        self.thumbnailDstDirPath = thumbnailDstDirPath
        self.thumbnailOriImgsList = os.listdir(thumbnailOriDirPath)


    # 等比例裁切做成缩略图 121：75 定宽
    def cutOff2ThumbnailSingle(self, imgName, srcDirPath, dstDirPath, scaleW=121, scaleH=75):
        imgSrc = srcDirPath + imgName
        img = Image.open(imgSrc)
        if (img is not None):
            img = img.resize((scaleW, scaleH), Image.ANTIALIAS)
            img.save(dstDirPath + imgName)

    # 对目录下的所有文件进行缩略图转换并放在缩略图目录下
    def cutOff2ThumbnailByDir(self):
        for imgName in self.thumbnailOriImgsList:
            self.cutOff2ThumbnailSingle(imgName=imgName, srcDirPath=self.thumbnailOriDirPath, dstDirPath=self.thumbnailDstDirPath, scaleW=121, scaleH=75)
