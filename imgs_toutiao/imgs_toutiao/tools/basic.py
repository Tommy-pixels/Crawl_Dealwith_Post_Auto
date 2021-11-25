from selenium import webdriver
import string
import zipfile
import random, time
import requests

'''
    返回毫秒级时间戳
'''
def getMilliSecond():
    return int(round(time.time() * 1000))

class cleanCookiesAndHeadersByRow():
    def translateCookies(self, row):
        cookieList = row.split(";")
        cookies = {}
        for item in cookieList:
            key = item.split("=")[0]
            val = item.split("=")[1]
            cookies[str(key).strip()] = str(val).strip()
        return cookies
    def translateHeaders(self, row):
        headerList = row.split("\n")
        headers = {}
        for item in headerList:
            key = item.split(":")[0].strip()
            if(key == 'Referer'):
                val = item[9:]
            else:
                try:
                    val = str(item).split(":")[1]
                except Exception as e:
                    print(e)

            if(key!=''):
                headers[key] = str(val).strip()
        return headers

# --------------------------- 爬取今日头条财经目录下所有图片的类 ----------------------------------
'''
    使用框架 selenium
    没有有url，获取文章的url
'''
class articleUrl_toutiao():

    # 代理服务器(产品官网 www.16yun.cn)
    proxyHost = "u7125.5.tp.16yun.cn"
    proxyPort = "6445"

    # 代理验证信息
    proxyUser = "16OINIUS"
    proxyPass = "971935"

    def create_proxy_auth_extension(self, scheme='http', plugin_path=None):
        if plugin_path is None:
            plugin_path = r'E:/yiniuyun/tmp/{}_{}@t.16yun.zip'.format(self.proxyUser, self.proxyPass)

        manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "16YUN Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                },
                "minimum_chrome_version":"22.0.0"
            }
            """

        background_js = string.Template(
            """
            var config = {
                mode: "fixed_servers",
                rules: {
                    singleProxy: {
                        scheme: "${scheme}",
                        host: "${host}",
                        port: parseInt(${port})
                    },
                    bypassList: ["localhost"]
                }
              };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                        username: "${username}",
                        password: "${password}"
                    }
                };
            }

            chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
            );
            """
        ).substitute(
            host=self.proxyHost,
            port=self.proxyPort,
            username=self.proxyUser,
            password=self.proxyPass,
            scheme=scheme,
        )

        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_path

    def start_agent(self):
        # 修改webdriver get属性
        # script = '''
        # Object.defineProperty(navigator, 'webdriver', {
        # get: () => undefined
        # })
        # '''
        # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        res = self.browser.get("http://httpbin.org/ip")
        return res

    def get_cookiesAndSignature(self, url="https://www.toutiao.com/"):
        proxy_auth_plugin_path = self.create_proxy_auth_extension()

        option = webdriver.ChromeOptions()
        option.add_argument("--start-maximized")
        # 如报错 chrome-extensions
        # option.add_argument("--disable-extensions")
        option.add_extension(proxy_auth_plugin_path)
        # 关闭webdriver的一些标志
        # option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(chrome_options=option,executable_path="E:\Projects\webDriver\\chrome\\chromedriver.exe")

        start_urls = url

        self.browser.get(start_urls)
        time.sleep(20)  # 等待
        # xhr重写
        js = """(function() {
                var proxied = window.XMLHttpRequest.prototype.open;
                let root = document.getElementById("root");
                let urlLinkNode = document.createElement("div");
                urlLinkNode.setAttribute("id", "urlLinkNode");
                root.appendChild(urlLinkNode);
                window.XMLHttpRequest.prototype.open = function() {
                    if(arguments[0]=='GET' && arguments[1].search("channel_id=3189399007")){
                        console.log(arguments);
                        let urlLinkNodeReal = document.getElementById("urlLinkNode")
                        urlLinkNodeReal.innerHTML = arguments[1];
                        return proxied.apply(this, [].slice.call(arguments));
                    }else{
                        return 0
                    }
                };
            })();"""
        # browser.execute_script(js)
        # 定位
        # caijing = browser.find_element_by_xpath("//div[@class='fix-header common-component-wrapper']//div[@class='feed-m-nav']/ul[@class='feed-default-nav']//li[@role='button'][4]")
        # time.sleep(2)
        # caijing.click()
        js2 = '''
                i = "https://www.toutiao.comhttps://tsearch.snssdk.com/search/suggest/hot_words/";
				n = window.byted_acrawler
				signature = n.sign(n,i)

				let root = document.getElementById("root");
                let urlLinkNode = document.createElement("div");
                urlLinkNode.setAttribute("id", "urlLinkNode");
                urlLinkNode.innerHTML = signature
                root.appendChild(urlLinkNode);
        '''
        self.browser.execute_script(js2)
        time.sleep(5)
        self.browser.execute_script(js2)


        # 获取最新signature
        signatureApi = self.browser.find_element_by_id("urlLinkNode").text
        print(signatureApi)
        signature = signatureApi
        # signature = str(signatureApi).split("signature=")[1]
        # refresh_count = str(signatureApi).split("refresh_count=")[1].split("&")[0]
        # 获取cookie
        dictCookies = self.browser.get_cookies()
        cookies = {}
        for item in dictCookies:
            key = item['name']
            cookies[str(key)] = str(item['value'])
        self.browser.close()
        return {
            # "refresh_count":refresh_count,
            "cookies":cookies,
            "signature":signature
        }

    def open(self):
        pass




# --------------------------- 随机时间休眠 ----------------------------------
# 随机时间
def randomSleep():
    sleepTime = random.randint(0,50)
    time.sleep(sleepTime)
    pass


# 已有图片链接下载图片的方法
def downimg(urlpath, imgname, dstDirPath):
    # 获取当前日期
    r = requests.get(urlpath)
    img = r.content       #响应的二进制文件
    with open(dstDirPath + str(imgname) + '.png','wb') as f:     #二进制写入
        f.write(img)






