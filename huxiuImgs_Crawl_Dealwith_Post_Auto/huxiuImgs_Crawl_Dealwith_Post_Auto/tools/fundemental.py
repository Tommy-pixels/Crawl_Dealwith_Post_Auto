import json
import os, time, requests, hashlib
from requests_toolbelt import MultipartEncoder


'''
    Post 图片的类
        参数：
            imgDirPath  处理完的图片目录路径dir   注意这里的路径最后加\\的
            
'''
class ImgPoster:
    def __init__(self, imgDirPath):
        self.imgDirPath = imgDirPath
        self.get_imgPathList()

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
        # print("修改MD5的文件：", imgSrc, "\n旧MD5: ", md5, " \t 新MD5： ", newMD5)

    # post发送单张图片
    def post_imgSingle(self, imgName, interface='http://121.40.187.51:8033/api/contentimgs_api'):
        userName = 'qin'
        password = 'qin123456'
        curTime = self.getCurTime()
        imgPath = self.imgDirPath + "\\" + imgName
        print("处理的路径： ", imgPath)
        # 改md5
        self.changeMD5(imgPath)
        # 打开图片
        # f = open('E:\Projects\imgReconization\imgsDontHasWaterMask\\2+商品-家居家装-吸顶灯 + 非自然图像-图像素材-图像素材.jpg', 'rb')
        f = open(imgPath, 'rb')
        # fileByte = base64.b64encode(f.read())  # 不要用这个，不然图片显示不了
        key = hashlib.md5(('datapool' + userName + password + str('20210826')).encode('utf-8')).hexdigest()
        # 这里传文件的时候用绝对路径传，不然传了之后显示不了
        formData = ({
            "key": key,
            "account": userName,
            "password": password,
            'file': (imgName, f, "image/jpeg")
        })
        m = MultipartEncoder(formData)
        headers2 = {
            "Content-Type": m.content_type
        }
        imgPostResult = requests.post(url=interface, data=m, headers=headers2)
        f.close()
        return imgPostResult

    # 发送目录下的所有所有图
    def updateImgs(self):
        for imgName in self.imgNameList:
            self.post_imgSingle(imgName)

    def updateImgsThumbnail(self):
        for imgName in self.imgNameList:
            self.post_imgSingle(imgName, interface='http://121.40.187.51:8033/api/thumbnail_api')