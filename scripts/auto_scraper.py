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
        self.max_articles_per_run = 5  # 首次测试，先设小一点
        
    async def scrape_url(self, crawler, url, source_name):
        """爬取单个URL - 简化版"""
        try:
            print(f"    正在爬取: {url}")
            
            config = CrawlerRunConfig(
                cache_mode="BYPASS",
                word_count_threshold=50,
                verbose=True,
            )
            
            result = await crawler.arun(url, config=config)
            
            if result.success and result.markdown:
                # 简单提取标题和内容
                lines = result.markdown.split('\n')
                title = lines[0] if lines else "无标题"
                # 去除可能的markdown标记
                title = title.replace('#', '').strip()
                content = '\n'.join(lines[1:])[:3000]
                
                if not content:
                    content = result.markdown[:3000]
                
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
        """生成文件名"""
        date = datetime.now().strftime("%Y%m%d")
        # 移除特殊字符，转小写
        slug = "".join(c for c in title if c.isalnum() or c == " ").lower()
        slug = "-".join(slug.split())[:50]
        return f"{date}-{slug}"
    
    async def run(self):
        """运行采集器"""
        print(f"\n{'='*50}")
        print(f"开始采集: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        article_count = 0
        
        # 配置浏览器
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
                        
                        if data and data.get("content") and len(data["content"]) > 100:
                            # 检查重复
                            if self.deduplicator.is_duplicate(data["title"], data["content"]):
                                print(f"  ⏭️ 文章已存在，跳过")
                                continue
                            
                            # 自动分类
                            category = self.classifier.classify(data["title"], data["content"])
                            data["category"] = category
                            
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
