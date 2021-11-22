# 爬取虎嗅网站时候需要知道的一些关键信息

## 1 栏目相关 下面是栏目的一些相关参数，在爬取对应栏目的时候需要其中的一些参数组合成cookie或是表单内容来获取数据。
    {    
        "success": true,
        "data": [{
            "channel_id": "10",
            "name": "视频",
            "sort_num": "0",
            "app_tab": 1
        }, {
            "channel_id": "21",
            "name": "车与出行",
            "sort_num": "30",
            "app_tab": 1
        }, {
            "channel_id": "106",
            "name": "年轻一代",
            "sort_num": "45",
            "app_tab": 1
        }, {
            "channel_id": "103",
            "name": "十亿消费者",
            "sort_num": "50",
            "app_tab": 1
        }, {
            "channel_id": "105",
            "name": "前沿科技",
            "sort_num": "55",
            "app_tab": 1
        }, {
            "channel_id": "115",
            "name": "财经",
            "sort_num": "10",
            "app_tab": 0
        }, {
            "channel_id": "22",
            "name": "娱乐淘金",
            "sort_num": "20",
            "app_tab": 0
        }, {
            "channel_id": "111",
            "name": "医疗健康",
            "sort_num": "55",
            "app_tab": 0
        }, {
            "channel_id": "113",
            "name": "文化教育",
            "sort_num": "60",
            "app_tab": 0
        }, {
            "channel_id": "114",
            "name": "出海",
            "sort_num": "65",
            "app_tab": 0
        }, {
            "channel_id": "102",
            "name": "金融地产",
            "sort_num": "70",
            "app_tab": 0
        }, {
            "channel_id": "110",
            "name": "企业服务",
            "sort_num": "75",
            "app_tab": 0
        }, {
            "channel_id": "2",
            "name": "创业维艰",
            "sort_num": "80",
            "app_tab": 0
        }, {
            "channel_id": "112",
            "name": "社交通讯",
            "sort_num": "85",
            "app_tab": 0
        }, {
            "channel_id": "107",
            "name": "全球热点",
            "sort_num": "90",
            "app_tab": 0
        }, {
            "channel_id": "4",
            "name": "生活腔调",
            "sort_num": "100",
            "app_tab": 0
        }],
        "message": "请求成功"
    } 

##　2　cookie相关
    1. cookie案例
        - 爬取财经栏目接口的文章信息
            cookies = {
                'huxiu_analyzer_wcy_id':'5wwrfvzxus44v5ozeuf5',
                'Hm_lvt_502e601588875750790bbe57346e972b':'1629765918,1629852279',
                'Hm_lpvt_502e601588875750790bbe57346e972b':'1629852754',
                'hx_object_visit_referer_11_115':'https%3A%2F%2Fwww.huxiu.com%2F',
                'SERVERID':'3e2292d3f2b396659e73250c9fef164b|' + str(curTime) + '|1629852277'
            }
        - 爬取车与出行栏目接口的文章信息
            huxiu_analyzer_wcy_id=5wwrfvzxus44v5ozeuf5; 
            Hm_lvt_502e601588875750790bbe57346e972b=1629765918,1629852279; 
            hx_object_visit_referer_11_10=https%3A%2F%2Fwww.huxiu.com%2Ftimeline%2F; 
            Hm_lpvt_502e601588875750790bbe57346e972b=1629869365; 
            hx_object_visit_referer_11_21=https%3A%2F%2Fwww.huxiu.com%2Ftimeline%2F; 
            SERVERID=3e2292d3f2b396659e73250c9fef164b|1629869364|1629852277
        注意到 hx_object_visit_referer_11_ 后面接的数字是对应栏目的id
        SERVERID 中间的那个时间戳是当前时间附近的时间戳，其它的没什么变化
    2. 表单相关
        formdata = {
            'platform': 'www',
            'last_time' :  '1629263760',
            'channel_id' : '115'
        }
        爬取的时候channel_id替换成对应的栏目id
    3. 接口爬出来的数据毕竟有限，要找找有没有其它可以爬到全部数据的接口。
        2021年8月25号这天爬取虎嗅网数据，这里能爬到的只有从 8月19号-4月16号 间的数据，再往后的接口就不返回数据了。
        爬取 车与出行 的时候发现没有上面这个问题，可能是虎嗅网本来就没有那么多财经的数据所有才没有返回数据的。

## 3 最后发请求时候要注意 表单信息里的 last_time，这个参数的值需要是能爬得到的最新数据的时间戳