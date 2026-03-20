# 采集源配置 - 修正版（只采集乌龟相关话题）
SOURCES = {
    "知乎": {
        "urls": [
            "https://www.zhihu.com/search?q=乌龟&type=content",  # 知乎搜索
            "https://www.zhihu.com/search?q=养龟&type=content",
            "https://www.zhihu.com/search?q=巴西龟&type=content",
            "https://www.zhihu.com/search?q=陆龟&type=content"
        ]
    },
    "B站": {
        "urls": [
            "https://search.bilibili.com/all?keyword=乌龟饲养",  # B站搜索
            "https://search.bilibili.com/all?keyword=龟病治疗",
            "https://search.bilibili.com/all?keyword=龟缸造景",
            "https://search.bilibili.com/all?keyword=陆龟",
            "https://search.bilibili.com/all?keyword=蛋龟"
        ]
    },
    "百度贴吧": {
        "urls": [
            "https://tieba.baidu.com/f?kw=乌龟",
            "https://tieba.baidu.com/f?kw=巴西龟",
            "https://tieba.baidu.com/f?kw=养龟"
        ]
    }
}
