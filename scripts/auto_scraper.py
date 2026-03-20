#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import os
import sys
import random
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
except ImportError:
    print("请先安装依赖: pip install crawl4ai playwright")
    sys.exit(1)

from config.sources import SOURCES
from deduplicator import ContentDeduplicator
from classifier import ArticleClassifier
from template import apply_article_template

class AutoScraper:
    def __init__(self):
        self.deduplicator = ContentDeduplicator("../data/articles_db.json")
        self.classifier = ArticleClassifier()
        self.output_dir = Path("../articles_new")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_articles_per_run = 10
        
    async def scrape_url(self, crawler, url, source_name):
        """爬取单个URL - 简化版"""
        try:
            config = CrawlerRunConfig(
                cache_mode="BYPASS",
                word_count_threshold=50,
                exclude_external_links=True,
            )
            
            result = await crawler.arun(url, config=config)
            
            if result.success and result.markdown:
                # 简单提取标题和内容
                lines = result.markdown.split('\n')
                title = lines[0] if lines else "无标题"
                content = '\n'.join(lines[1:])[:3000]
                
                return {
                    "title": title,
                    "content": content,
                    "url": url,
                    "source": source_name,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": []
                }
            else:
                return None
                
        except Exception as e:
            print(f"  处理异常: {url} - {str(e)}")
            return None
    
    def generate_filename(self, title):
        """生成文件名"""
        date = datetime.now().strftime("%Y%m%d")
        slug = "".join(c for c in title if c.isalnum() or c == " ").lower()
        slug = "-".join(slug.split())[:50]
        return f"{date}-{slug}"
    
    async def run(self):
        """运行采集器"""
        print(f"\n{'='*50}")
        print(f"开始采集: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        article_count = 0
        
        browser_config = BrowserConfig(headless=True)
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for source_name, source_config in SOURCES.items():
                if article_count >= self.max_articles_per_run:
                    break
                    
                print(f"\n📡 正在采集 {source_name}...")
                
                for url in source_config.get("urls", []):
                    if article_count >= self.max_articles_per_run:
                        break
                        
                    print(f"  🔗 访问: {url}")
                    
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    data = await self.scrape_url(crawler, url, source_name)
                    
                    if data and data.get("content"):
                        # 检查重复
                        if self.deduplicator.is_duplicate(data["title"], data["content"]):
                            print(f"  ⏭️ 文章已存在，跳过")
                            continue
                        
                        # 自动分类
                        category = self.classifier.classify(data["title"], data["content"])
                        data["category"] = category
                        
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
        
        print(f"\n{'='*50}")
        print(f"采集完成！共新增 {article_count} 篇文章")
        print(f"文件保存在: {self.output_dir.absolute()}")
        print(f"{'='*50}")

async def main():
    scraper = AutoScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
