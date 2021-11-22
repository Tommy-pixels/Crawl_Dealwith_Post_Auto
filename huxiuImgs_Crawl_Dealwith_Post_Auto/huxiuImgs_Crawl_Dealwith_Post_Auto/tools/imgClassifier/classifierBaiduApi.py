# encoding:utf-8

from aip import AipImageClassify
import requests
import base64
from tools import basic
import os

'''
通用物体和场景识别
'''
class imgsClassifier():
    def __init__(self, crawledDirPath, savedDirPath):
        self.request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
        """ 你的 APPID AK SK """
        self.APP_ID = '24654559'
        self.API_KEY = 'Pnexi1A99Eobsb1iX7xiBTsE'
        self.SECRET_KEY = 'qYYXNhsGLrnAwAWkmHPFOEofQHPRqSYL'
        self.crawledDirPath = crawledDirPath #存放刚刚爬取下来的图片的路径
        self.savedDirPath = savedDirPath
        self.get_imgPathList()

    def get_imgPathList(self):
        # 获取目录下所有文件的路径列表
        imgNameList = os.listdir(self.crawledDirPath)  # 获取目录下的所有文件名
        imgPathList = []
        for imgName in imgNameList:
           item = self.crawledDirPath + '\\' + imgName
           imgPathList.append(item)
        self.imgNameList = imgNameList
        return imgNameList

    def reconizeSingleImgFunc(self, imgName, imgSavedDirPath, request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"):
        imgSuffix = '.jpg'
        # imgSrcPath = self.crawledDirPath + imgName + imgSuffix
        imgSrcPath = self.crawledDirPath + imgName

        # 二进制方式打开图片文件
        f = open(imgSrcPath, 'rb')
        img = base64.b64encode(f.read())

        params = {"image":img}
        access_token = basic.getAccessToken(self.API_KEY, self.SECRET_KEY)
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}


        response = requests.post(request_url, data=params, headers=headers)
        f.close()
        response = response.json()
        print(response)

        if("result" in response):
            result = response["result"]
            result_num = response['result_num']
            # 不收录root只要keyword
            if(result_num >= 2):
                lis = []
                lis.append(result[0]["keyword"])
                lis.append(result[1]["keyword"])
                name = lis[0] + ' - ' + lis[1]
                reconizedName = '_' + name #采用权重最大头俩个的来命名
            elif(result_num == 1):
                reconizedName = '_' + result[0]["keyword"]
            else:
                reconizedName = ''
            # imgDstPath = imgSavedDirPath + imgName + reconizedName + imgSuffix
            imgDstPath = imgSavedDirPath + imgName.replace('.png','') + reconizedName + '.png'
            try:
                basic.reName(imgSrcPath, imgDstPath)
            except Exception as e:
                pass

    def reconizeImgs(self):
        for imgName in self.imgNameList:
            self.reconizeSingleImgFunc(imgName=imgName, imgSavedDirPath=self.savedDirPath)

    def run(self):
        self.reconizeImgs()


# for imgNum in range(5153, 5782):
#     reconizeFunc(imgNum, request_url)



