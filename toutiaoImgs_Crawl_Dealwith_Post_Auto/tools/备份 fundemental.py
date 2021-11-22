import json
import os, time, requests, hashlib
import base64
import urllib.parse
from urllib import request

'''
    Post 图片的类
        参数：
            imgDirPath  图片目录路径dir   注意这里的路径最后是不加\\的

'''


class ImgPoster:
    def __init__(self, imgDirPath):
        self.imgDirPath = imgDirPath

    # 获取目录下所有文件的路径列表
    def get_imgPathList(self):
        imgNameList = os.listdir(self.imgDirPath)  # 获取目录下的所有文件名
        imgPathList = []
        for imgName in imgNameList:
            item = self.imgDirPath + '\\' + imgName
            imgPathList.append(item)
        self.imgNameList = imgNameList
        return imgNameList

    # 获取时间戳
    def getCurTime(self):
        return int(round(time.time()))

    # 修改单张图片的md5
    def changeMD5(self, imgSrc):
        with open(imgSrc, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        file = open(imgSrc, 'rb').read()
        with open(imgSrc, 'wb') as new_file:
            new_file.write(file + bytes('\0', encoding='utf-8'))  # here we are adding a null to change the file content
            newMD5 = hashlib.md5(open(imgSrc, 'rb').read()).hexdigest()
        print("修改MD5的文件：", imgSrc, "\n旧MD5: ", md5, " \t 新MD5： ", newMD5)

    # post发送单张图片
    def post_imgSingle(self, imgName, interface='http://121.40.187.51:8033/api/contentimgs_api'):
        userName = 'qin'
        password = 'qin123456'
        curTime = self.getCurTime()
        imgPath = self.imgDirPath + "\\" + imgName
        # 改md5
        self.changeMD5(imgPath)
        # 打开图片
        f = open(imgPath, 'rb')
        fileByte = base64.b64encode(f.read())
        # imgFile  = fileByte.decode('ascii')
        key = hashlib.md5(('datapool' + userName + password + str('20210819')).encode('utf-8')).hexdigest()
        formData = {
            "key": key,
            "account": userName,
            "password": password,
        }
        files = {
            'file': (imgName, fileByte, "image/jpeg")
            # 'file': (imgName, fileByte)
        }
        imgPostResult = requests.post(url=interface, files=files, data=formData)
        f.close()
        return imgPostResult