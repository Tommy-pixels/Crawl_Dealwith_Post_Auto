import time

# 针对哔哩哔哩网站
def getCidBySelenium(browser, url):
    browser.get(url)
    time.sleep(1)
    js = 'return cid'  # js语句 需要返回值 所以加上了return
    cid = browser.execute_script(js)  # 执行js的方法
    cookieList = browser.get_cookies()
    cookies = {}
    for item in cookieList:
        cookies[item['name']] = item['value']
    return (cid, cookies)


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