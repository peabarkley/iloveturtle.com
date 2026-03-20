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

# 尝试导入 crawl4ai，如果失败则给出友好提示
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
        self.max_articles_per_run = 8  # 每次最多采集8篇
        
        # 乌龟相关关键词（用于过滤内容）
        self.turtle_keywords = [
            '乌龟', '养龟', '龟', '巴西龟', '陆龟', '水龟', 
            '蛋龟', '麝香', '草龟', '剃刀', '窄桥', '黄缘',
            '冬眠', '龟缸', '腐皮', '肺炎', '白眼病', '软壳',
            '晒背', 'UVB', '加热', '过滤', '造景', '生态缸',
            'turtle', 'tortoise', 'slider', 'musk'
        ]
        
        # 黑名单词（过滤导航菜单）
        self.blacklist = [
            '首页', '番剧', '直播', '游戏中心', '会员购', 
            '漫画', '赛事', '下载客户端', '搜索', '筛选', 
            '分区', '粉丝', '关注', '登录', '注册', '投稿',
            '消息', '动态', '收藏', '历史', '创作中心',
            '反馈', '客服', '帮助', '协议', '隐私政策'
        ]
    
    def is_turtle_related(self, text):
        """检查内容是否与乌龟相关"""
        text_lower = text.lower()
        for kw in self.turtle_keywords:
            if kw.lower() in text_lower:
                return True
        return False
    
    def extract_title_from_html(self, markdown_content, url):
        """从Markdown内容中提取标题（改进版）"""
        lines = markdown_content.split('\n')
        
        # 方法1：找第一个h1标题（以#开头的行）
        for line in lines[:30]:
            if line.startswith('# '):
                title = line[2:].strip()
                # 检查是否包含黑名单词
                if any(bad in title for bad in self.blacklist):
                    continue
                # 检查是否与乌龟相关
                if self.is_turtle_related(title):
                    if title and len(title) > 5 and len(title) < 100:
                        return title[:60]
        
        # 方法2：找第一个非空行，且不是导航菜单
        for line in lines[:20]:
            clean_line = line.strip()
            if clean_line and not clean_line.startswith('![') and len(clean_line) > 10:
                # 检查是否包含黑名单词
                if any(bad in clean_line for bad in self.blacklist):
                    continue
                # 检查是否像菜单（包含太多|符号）
                if clean_line.count('|') > 3:
                    continue
                # 检查是否与乌龟相关
                if self.is_turtle_related(clean_line):
                    return clean_line[:60]
        
        # 方法3：从URL中提取关键词
        if 'keyword=' in url:
            keyword = url.split('keyword=')[-1].split('&')[0]
            if keyword:
                return f"{keyword}相关资讯"
        
        # 方法4：尝试从内容中找第一个乌龟相关句子
        for line in lines[:50]:
            if self.is_turtle_related(line):
                clean_line = line.strip()[:60]
                if len(clean_line) > 10:
                    return clean_line
        
        return "乌龟科普文章"
    
    async def scrape_url(self, crawler, url, source_name):
        """爬取单个URL - 简化版（不依赖OpenAI）"""
        try:
            print(f"    正在爬取: {url}")
            
            config = CrawlerRunConfig(
                cache_mode="BYPASS",
                word_count_threshold=50,
                verbose=True,
            )
            
            result = await crawler.arun(url, config=config)
            
            if result.success and result.markdown:
                # 检查内容是否包含乌龟相关关键词
                if not self.is_turtle_related(result.markdown):
                    print(f"    内容无关乌龟，跳过")
                    return None
                
                # 提取标题
                title = self.extract_title_from_html(result.markdown, url)
                
                # 提取内容（取前4000字）
                content = result.markdown[:4000]
                
                # 清理内容中的多余空白
                content = re.sub(r'\n{3,}', '\n\n', content)
                
                return {
                    "title": title,
                    "content": content,
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
        """生成文件名 - 使用标题拼音/英文"""
        date = datetime.now().strftime("%Y%m%d")
        
        # 移除特殊字符，只保留字母数字和空格
        clean_title = re.sub(r'[^\w\s-]', '', title)
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
                        
                        # 随机延迟，避免被封
                        await asyncio.sleep(random.uniform(2, 4))
                        
                        data = await self.scrape_url(crawler, url, source_name)
                        
                        if data and data.get("content") and len(data["content"]) > 200:
                            # 检查重复
                            if self.deduplicator.is_duplicate(data["title"], data["content"]):
                                print(f"  ⏭️ 文章已存在，跳过")
                                continue
                            
                            # 自动分类
                            category = self.classifier.classify(data["title"], data["content"])
                            data["category"] = category
                            
                            print(f"  📝 标题: {data['title'][:30]}...")
                            print(f"  📝 分类: {category}")
                            
                            # 生成文件名
                            base_filename = self.generate_filename(data["title"])
                            
                            # 生成中英文版本
                            zh_html = apply_article_template(data, "zh")
                            zh_path = self.output_dir / f"{base_filename}.zh.html"
                            with open(zh_path, "w", encoding="utf-8") as f:
                                f.write(zh_html)
                            
                            en_html = apply_article_template(data, "en")
                            en_path = self.output_dir / f"{base_filename}.en.html"
                            with open(en_path, "w", encoding="utf-8") as f:
                                f.write(en_html)
                            
                            # 添加到数据库
                            self.deduplicator.add_article(data)
                            
                            article_count += 1
                            print(f"  ✅ 已保存: {data['title'][:30]}... ({article_count}/{self.max_articles_per_run})")
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
