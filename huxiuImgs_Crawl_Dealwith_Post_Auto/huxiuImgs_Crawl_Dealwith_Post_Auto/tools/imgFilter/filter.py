#-*-coding:utf-8-*-
import os, re
import cv2
import numpy as np
from tools import basic
from PIL import Image

'''
    dirPath : 存放待处理的图片的目录路径
        关键词过滤
        水印过滤
        水印处理-图片裁切
'''
class imgsFilter():
    def __init__(self, imgsDontHasWaterMaskDir, imgDirHasWaterMask, imgCleanedStep1, dirOriPath="E:\Projects\imgReconization\imgs\\"):
        self.imgDirPath = dirOriPath  # 存放图片的目录路径
        self.imgNameList = os.listdir(dirOriPath) # 获取目录下所有图片的名字
        self.containFilterStrImgPathList = []   # 含有表格俩字的图片路径的列表
        self.cleanedImgsList = os.listdir(dirOriPath)   # 经过清洗后的图片的路径列表
        self.cleanedImgsListIsChanged = False   # 判断是否经过过滤
        self.imgNameListHasWaterMask = []   # 含有水印的图片列表
        self.imgNameListHasNoWaterMask = [] # 不含有水印的图片列表
        self.containFilterStrImgPathList = []
        self.imgCleanedStep1 = imgCleanedStep1     # 用于保存经过初步筛选（处理水印之前）的图片的目录
        self.imgDirHasWaterMask = imgDirHasWaterMask    # 用于保存含有水印的图片的目录
        self.imgDirDontHasWaterMask = imgsDontHasWaterMaskDir


    # --------------------- 1 图片过滤 依据命名关键词过滤图片 ---------------------------------------------
    # 过滤掉含指定字符 filterStr 的的不通用图片的路径 默认过滤掉表格
    def filterStr(self, filterStr = '表格'):
        self.cleanedImgsListIsChanged = True
        for imgName in self.cleanedImgsList:
            # 过滤掉命名全部为数字，没有关键字的图片
            name = imgName.split(".")[0]
            if(basic.checkIfAllNumber(name)):
                # 全为数字则过滤
                if (imgName not in self.containFilterStrImgPathList):
                    self.containFilterStrImgPathList.append(imgName)
            else:
                if(re.search(filterStr, imgName)):
                    if(imgName not in self.containFilterStrImgPathList):
                        self.containFilterStrImgPathList.append(imgName)


    # 依据关键词过滤掉不能用的图片
    def filterStrList(self, filterStrList = [
        '图表','表格', '截图', '走势图', '书本','数学试卷','说明书','文字图片','图画', '彩色动漫', '便签纸', '评定表', '食谱','电视背景墙','竞买申请书','抛光砖','进口货物报关单','小窝','报纸杂志',
        '手抄报','公共标示','行政区划图','电路图','专业招生简章','成绩单','报告单','派车单','网页导航','简历模板','电脑刷','名片','中国建设银行',
        '中国银行','医药标志','卡巴斯基软件','数学图形','投资银行面试指南','通知书','二维码','简笔画','家用电器','亲吻','表彰会','简报','英语字母','圆珠笔',
        '图标','毛笔','车标','书籍封面','头发','计算器','会刊广告','升国旗','地图','彩票','卡通动漫人物','信用卡','旗帜','平板手机','pvc卡','广告',
        '网址','曲谱','东芝','玩具','电纸书','放大镜','头饰','工笔画','交通路牌','交通标志','t恤','手提包','瓶子','戒指', '显示器屏幕'
    ]):
        self.cleanedImgsListIsChanged = True
        for filterStr in filterStrList:
            self.filterStr(filterStr)
        self.setCleanedImgsList()

    # --------------------- 2 图片过滤 依据图片的尺寸过滤图片 ---------------------------------------------
    # 基础过滤
    def filterNoneFile(self):
        for imgName in self.cleanedImgsList:
            imgSrc = self.imgDirPath + imgName
            img = cv2.imdecode(np.fromfile(imgSrc, dtype=np.uint8), -1)
            if(img is None):
                # 过滤掉打不开的图片
                self.cleanedImgsList.pop(self.cleanedImgsList.index(imgName))
            else:
                if(img.shape[0]<300):
                    # 过滤掉高度很小的图片
                    self.cleanedImgsList.pop(self.cleanedImgsList.index(imgName))

    def filterImgBySizeSingle(self, imgName, imgSrc):
        # 打开图片
        img = cv2.imdecode(np.fromfile(imgSrc, dtype=np.uint8), -1)
        if(img is not None):
            # 获取图片宽高
            height = img.shape[0]
            width = img.shape[1]
            # 判断图片宽高是否满足要求
            if (height < 300):
                return {
                    "check": True,
                    "imgSrc": imgSrc
                }
            else:
                return {
                    "check": False,
                    "imgSrc": imgSrc
                }
        else:
            # 若图片读取不了也过滤掉
            self.cleanedImgsList.pop(self.cleanedImgsList.index(imgName))
            return -1


    def filterImgBySizeAll(self):
        for imgName in self.cleanedImgsList:
            imgSrc = self.imgDirPath + imgName
            result = self.filterImgBySizeSingle(imgName,imgSrc)
            if(result!=-1 and result["check"]):
                # result为true则该图片过滤掉
                index = self.cleanedImgsList.index(imgName)
                self.cleanedImgsList.pop(index)
            else:
                # result为false则该图片保留
                pass

    # --------------------- 3 水印处理 ---------------------------------------------
    '''
        通过识别水印的方式貌似不是那么好，直接采用裁切的形式把水印去掉吧，当然这个方法也不是完美，当至少不会那么麻烦
        判断单张图片是否含有水印 采用cv2的模板匹配方法
    '''
    def checkIfHasWatermarkSingle(self, imgName, imgDirPath="E:\Projects\imgReconization\imgs\\", templateSrc="E:\Projects\imgReconization\dontDelete\\templatePerfectOne28.png"):
        # 获取水印目录下所有水印路径
        templateNameList = os.listdir('E:\Projects\imgReconization\dontDelete\\')
        templatePathList = []
        for item in templateNameList:
            templatePathList.append('E:\Projects\imgReconization\dontDelete\\' + item)

        # img_rgb = cv2.imread(imgSrc)  # 路径含有中文名不能直接用这个，要用下面那个转换
        imgSrc = imgDirPath + imgName
        img_rgb = cv2.imdecode(np.fromfile(imgSrc, dtype=np.uint8), -1)  # Read the main image
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)    # Convert it to grayscale



        def cvReconize(img_gray, templatePath):
            res = cv2.matchTemplate(img_gray, templatePath, cv2.TM_CCOEFF_NORMED)  # Perform match operations.
            return res


        threshold = 0.38 # Specify a threshold 0.35本来挺好的
        for templateSrc in templatePathList:
            # 根据图片的尺寸来选择合适的模板

            template = cv2.imread(templateSrc, 0)  # Read the template
            w, h = template.shape[::-1]  # Store width and heigth of template in w and h

            res = cvReconize(img_gray, template)
            loc = np.where(res >= threshold)    # Store the coordinates of matched area in a numpy array
            x = loc[0]
            y = loc[1]
            # Draw a rectangle around the matched region.
            if(len(x) and len(y)):
                for pt in zip(*loc[::-1]):
                    # pt[0]表示水印位置所在的像素高度
                    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)
                    # Show the final image with the matched area.
                    cv2.imwrite("E:\Projects\imgReconization\\reconizeWaterMaskResult\\test_001.png", img_rgb)
                    waterMaskLocY = pt[1]
                print("I found the watermark: ", imgSrc, "水印位置： x= ",x, " y= ",y, "对应模板：", templateSrc)
                return {
                    "hasWaterMask" : True,
                    "imgName" : imgName,
                    "waterMaskLocY": waterMaskLocY      # 水印位置的y坐标
                }
            else:
                print('there is no watermark', imgSrc)
                # return {
                #     "hasWaterMask" : False,
                #     "imgName" : imgName
                # }
                print({
                    "hasWaterMask" : False,
                    "imgName" : imgName
                })
                continue
        print("没有对应的水印模板或无水印")
        return {
            "hasWaterMask" : False,
            "imgName" : imgName
        }

    # 将经过筛选的所有图片依据是否有水印进行分类
    def classifyImgsListByWaterMask(self):
        for imgName in self.cleanedImgsList:
            try:
                result = self.checkIfHasWatermarkSingle(imgName, self.imgDirPath)
                if(result["hasWaterMask"]):
                    self.imgNameListHasWaterMask.append(result["imgName"])
                    src = self.imgDirPath + imgName
                    dst = self.imgDirHasWaterMask + imgName
                    basic.copyFile(src, dst)
                    # 对水印进行裁切
                    waterMaskY = result["waterMaskLocY"]
                    imgHeight = self.get_imgHeight(src)
                    cutBottomHeight = imgHeight - waterMaskY
                    self.cutOffWaterMaskSingle(imgSrc=dst, cutBottomHeight=cutBottomHeight)
                else:
                    self.imgNameListHasNoWaterMask.append(result["imgName"])
                    src = self.imgDirPath + imgName
                    dst = self.imgDirDontHasWaterMask + imgName
                    basic.copyFile(src, dst)
            except Exception as E:
                print(E)

    # --------------------- 4 图片裁切 ---------------------------------------------
    # 获取图片的高度
    def get_imgHeight(self, imgSrc):
        img = cv2.imdecode(np.fromfile(imgSrc, dtype=np.uint8), -1)
        h = img.shape[0]
        return h

    # 单张图片的裁切 用cv2
    def cutOffWaterMaskSingle(self, imgSrc, cutBottomHeight=55):
        # img = cv2.imread(imgSrc)
        img = cv2.imdecode(np.fromfile(imgSrc, dtype=np.uint8), -1)
        if(img is not None):
            try:
                h = img.shape[0]
                w = img.shape[1]
                cutHeight = h - cutBottomHeight
                cutWidth = w
                print(img.shape)
                print(cutWidth, ":", cutHeight)
                cropped = img[0:cutHeight, 0:cutWidth]  # 裁剪坐标为[y0:y1, x0:x1]
                # cv2.imwrite(imgSrc, cropped) #这种方式保存命名中文会乱码
                cv2.imencode('.jpg', cropped)[1].tofile(imgSrc)
            except:
                print(cropped)
                print(imgSrc)

    # 对目录下的所有文件进行裁切并覆盖
    def cutOffWaterMaskByDir(self, cutBottomHeight=55):
        for imgName in self.cleanedImgsList:
            imgSrc = self.imgCleanedStep1 + imgName
            self.cutOffWaterMaskSingle(imgSrc, cutBottomHeight)


    # --------------------- 5 以下为set操作 ---------------------------------------------
    # 设置经过清洗的图片路径列表 本方法用于关键词过滤 见1
    def setCleanedImgsList(self):
        self.cleanedImgsListIsChanged = True
        for imgItem in self.containFilterStrImgPathList:
            delIndex = self.cleanedImgsList.index(imgItem)
            self.cleanedImgsList.pop(delIndex)

    # 将经过初步过滤的图片复制到新的目录下
    def setCopyCleanedImgsList(self):
        for imgName in self.cleanedImgsList:
            src = self.imgDirPath + imgName
            dst = self.imgCleanedStep1 + imgName
            basic.copyFile(src, dst)

    # --------------------- 6 以下为get操作 ---------------------------------------------
    # 获取含有指定字符串的图片路径列表
    def getImgPathContain(self, filteStr):
        if(self.containFilterStrImgPathList):
            return self.containFilterStrImgPathList
        else:
            return '不存在含有 {} 的路径'.format(filteStr)

    # 获取经过清洗后的图片路径列表
    def getCleanedImgsList(self):
        if(self.cleanedImgsListIsChanged):
            return self.cleanedImgsList
        else:
            return '图片路径未经过清洗'

    def run_byWaterMask(self):
        # 水印识别过滤的整个步骤集成
        # 关键词过滤
        self.filterStrList()
        # 过滤掉打不开的图片
        self.filterNoneFile()
        # 尺寸过滤
        self.filterImgBySizeAll()
        # 将经过初步过滤的图片复制到新的目录下
        self.setCopyCleanedImgsList()
        # 水印裁切
        self.classifyImgsListByWaterMask()


    def run(self):
        # 过滤的整个步骤集成
        # 关键词过滤
        self.filterStrList()
        # 过滤掉打不开的图片
        self.filterNoneFile()
        # 尺寸过滤
        # self.filterImgBySizeAll()
        # 将经过初步过滤的图片复制到新的目录下
        self.setCopyCleanedImgsList()
        # 水印裁切
        # self.cutOffWaterMaskByDir()

    def run_(self):
        # 过滤的整个步骤集成
        # 关键词过滤
        self.filterStrList()
        # 过滤掉打不开的图片
        self.filterNoneFile()
        # 将经过初步过滤的图片复制到新的目录下
        self.setCopyCleanedImgsList()






