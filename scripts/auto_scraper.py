#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os
import sys
import random
import re
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 尝试导入 crawl4ai
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError as e:
    print(f"❌ 导入 crawl4ai 失败: {e}")
    print("请运行: pip install crawl4ai playwright")
    CRAWL4AI_AVAILABLE = False
    sys.exit(1)

# 导入自定义模块
try:
    from config.sources import SOURCES
    from deduplicator import ContentDeduplicator
    from classifier import ArticleClassifier
    from template import apply_article_template
except ImportError as e:
    print(f"❌ 导入自定义模块失败: {e}")
    print("请确保以下文件存在:")
    print("  - scripts/config/sources.py")
    print("  - scripts/deduplicator.py")
    print("  - scripts/classifier.py")
    print("  - scripts/template.py")
    sys.exit(1)

class AutoScraper:
    def __init__(self):
        self.deduplicator = ContentDeduplicator("../data/articles_db.json")
        self.classifier = ArticleClassifier()
        self.output_dir = Path("../articles_new")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_articles_per_run = 5  # 每次最多采集5篇
        
        # 导航菜单关键词（用于过滤）
        self.nav_keywords = [
            '首页', '番剧', '直播', '游戏中心', '会员购', '漫画', '赛事',
            '下载客户端', '搜索', '筛选', '分区', '粉丝', '关注', '登录',
            '注册', '投稿', '消息', '动态', '收藏', '历史', '反馈', '客服',
            '综合排序', '最多播放', '最新发布', '弹幕', '全站', '排行榜',
            '活动', '课堂', '创作中心', '帮助', '协议', '隐私政策',
            'space.bilibili.com', 'hdslb.com', 'bilibili.com', 'tieba.baidu.com',
            '知乎', '回答', '提问', '写文章', '发现', '等你来答',
            '打开App', '流畅', '高清', '超清', '会员', '大会员',
            '视频详情', '相关推荐', '评论', '点赞', '分享', '收藏',
            '违法和不良信息举报电话', '网上有害信息举报', '涉未成年人举报'
        ]
        
        # 乌龟相关关键词
        self.turtle_keywords = [
            '乌龟', '养龟', '巴西龟', '陆龟', '水龟', '蛋龟', '麝香', 
            '剃刀', '窄桥', '草龟', '花龟', '黄缘', '闭壳龟', '苏卡达',
            '赫曼', '红腿', '豹龟', '辐射', '缅陆', '鳄龟', '枫叶龟',
            '锯缘', '安布', '木纹龟', '冬眠', '龟缸', '造景', '过滤',
            'UVB', '晒背', '腐皮', '肺炎', '白眼病', '软壳', '浮水',
            '加热', '温度', '水质', '喂食', '龟粮', '活食', '蚯蚓',
            'turtle', 'tortoise', 'slider', 'musk', 'sulcata', 'hermann'
        ]
    
    def clean_content(self, text):
        """清理内容，去除导航菜单等无关内容"""
        lines = text.split('\n')
        cleaned_lines = []
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
                
            # 跳过太短的行
            if len(line) < 6:
                continue
                
            # 跳过包含导航关键词的行
            if any(kw in line for kw in self.nav_keywords):
                continue
                
            # 跳过URL行
            if line.startswith('http') or '.com' in line or '.cn' in line:
                continue
                
            # 跳过包含太多符号的行
            if line.count('{') > 2 or line.count('}') > 2 or line.count('*') > 3:
                continue
                
            # 跳过全是数字和符号的行
            if re.match(r'^[\d\s\-_+=*&^%$#@!~`|\\/\[\]{}()<>]+$', line):
                continue
                
            # 检查是否包含中文字符
            if re.search(r'[\u4e00-\u9fff]', line):
                # 检查是否与乌龟相关
                if any(kw in line for kw in self.turtle_keywords):
                    cleaned_lines.append(line)
                    meaningful_lines.append(line)
                else:
                    # 如果没有乌龟关键词但长度合适，也保留
                    if 10 < len(line) < 100:
                        cleaned_lines.append(line)
        
        # 如果没有找到任何乌龟相关内容，返回空
        if len(meaningful_lines) < 2:
            return ""
            
        return '\n\n'.join(cleaned_lines[:30])
    
    def extract_title(self, url, content):
        """从内容中提取标题 - 改进版"""
        lines = content.split('\n')
        
        # 优先找包含乌龟关键词的行
        for line in lines[:20]:
            line = line.strip()
            # 跳过太短或太长的行
            if len(line) < 8 or len(line) > 100:
                continue
            # 跳过导航关键词
            if any(kw in line for kw in self.nav_keywords):
                continue
            # 如果包含乌龟关键词，优先作为标题
            if any(kw in line for kw in self.turtle_keywords):
                # 清理多余符号
                title = re.sub(r'^[#\s*【】\[\]「」]+', '', line)
                title = re.sub(r'[#\s*【】\[\]「」]+$', '', title)
                return title[:50]
        
        # 如果没有找到，找第一个有意义的行
        for line in lines[:15]:
            line = line.strip()
            if len(line) < 8 or len(line) > 100:
                continue
            if any(kw in line for kw in self.nav_keywords):
                continue
            if re.search(r'[\u4e00-\u9fff]', line):
                title = re.sub(r'^[#\s*]+', '', line)
                return title[:50]
        
        # 从URL中提取
        if 'video/BV' in url:
            return "B站乌龟视频"
        elif 'zhuanlan' in url:
            return "知乎乌龟文章"
        elif 'tieba' in url:
            return "贴吧乌龟帖子"
        elif 'bilibili' in url:
            return "B站乌龟内容"
        elif 'zhihu' in url:
            return "知乎乌龟内容"
        else:
            return "乌龟科普文章"
    
    def is_turtle_related(self, text):
        """检查内容是否与乌龟相关"""
        if not text:
            return False
        text_lower = text.lower()
        for kw in self.turtle_keywords:
            if kw.lower() in text_lower:
                return True
        return False
    
    async def scrape_url(self, crawler, url, source_name):
        """爬取单个URL"""
        try:
            print(f"    正在爬取: {url}")
            
            config = CrawlerRunConfig(
                cache_mode="BYPASS",
                word_count_threshold=50,
                verbose=True,
            )
            
            result = await crawler.arun(url, config=config)
            
            if result.success and result.markdown:
                # 检查是否与乌龟相关
                if not self.is_turtle_related(result.markdown):
                    print(f"    内容无关乌龟，跳过")
                    return None
                
                # 清理内容
                cleaned_content = self.clean_content(result.markdown)
                
                if len(cleaned_content) < 100:
                    print(f"    内容过短，跳过")
                    return None
                
                # 提取标题
                title = self.extract_title(url, cleaned_content)
                
                print(f"    找到标题: {title}")
                
                return {
                    "title": title,
                    "content": cleaned_content,
                    "url": url,
                    "source": source_name,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": []
                }
            else:
                print(f"    爬取失败: {url}")
                return None
                
        except Exception as e:
            print(f"    处理异常: {url} - {str(e)}")
            return None
    
    def generate_filename(self, title):
        """生成文件名 - 使用标题"""
        date = datetime.now().strftime("%Y%m%d")
        # 移除特殊字符，只保留字母数字和空格
        clean_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
        # 转小写，空格变中划线
        slug = clean_title.lower().strip().replace(' ', '-')
        # 限制长度
        slug = slug[:50]
        
        # 如果slug为空，用时间戳
        if not slug or len(slug) < 3:
            import time
            slug = f"article-{int(time.time())}"
        
        return f"{date}-{slug}"
    
    async def run(self):
        """运行采集器"""
        print(f"\n{'='*50}")
        print(f"开始采集: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        article_count = 0
        
        browser_config = BrowserConfig(
            headless=True,
            verbose=True,
        )
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for source_name, source_config in SOURCES.items():
                    if article_count >= self.max_articles_per_run:
                        break
                        
                    print(f"\n📡 正在采集 {source_name}...")
                    
                    for url in source_config.get("urls", []):
                        if article_count >= self.max_articles_per_run:
                            break
                            
                        print(f"  🔗 访问: {url}")
                        
                        # 随机延迟
                        await asyncio.sleep(random.uniform(3, 5))
                        
                        data = await self.scrape_url(crawler, url, source_name)
                        
                        if data and data.get("content") and len(data["content"]) > 200:
                            # 检查重复
                            if self.deduplicator.is_duplicate(data["title"], data["content"]):
                                print(f"  ⏭️ 文章已存在，跳过")
                                continue
                            
                            # 自动分类
                            category = self.classifier.classify(data["title"], data["content"])
                            data["category"] = category
                            
                            print(f"  📝 标题: {data['title']}")
                            print(f"  📝 分类: {category}")
                            
                            # 生成文件名
                            base_filename = self.generate_filename(data["title"])
                            
                            # 生成中文版
                            zh_html = apply_article_template(data, "zh")
                            zh_path = self.output_dir / f"{base_filename}.zh.html"
                            with open(zh_path, "w", encoding="utf-8") as f:
                                f.write(zh_html)
                            
                            # 添加到数据库
                            self.deduplicator.add_article(data)
                            
                            article_count += 1
                            print(f"  ✅ 已保存 ({article_count}/{self.max_articles_per_run})")
                        else:
                            print(f"  ⚠️ 内容过短或无效，跳过")
        
        except Exception as e:
            print(f"❌ 采集过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        print(f"\n{'='*50}")
        print(f"采集完成！共新增 {article_count} 篇文章")
        print(f"文件保存在: {self.output_dir.absolute()}")
        print(f"{'='*50}")

async def main():
    scraper = AutoScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
