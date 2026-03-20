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
        
    def extract_title_from_html(self, markdown_content, url):
        """从Markdown内容中提取标题（不依赖OpenAI）"""
        lines = markdown_content.split('\n')
        
        # 方法1：找第一个h1标题（以#开头的行）
        for line in lines[:15]:  # 只检查前15行
            if line.startswith('# '):
                # 移除#和空格，取前60个字符
                title = line[2:].strip()
                if title and len(title) > 5:
                    return title[:60]
        
        # 方法2：找第一个非空行（可能没有#标记）
        for line in lines[:10]:
            if line.strip() and not line.startswith('![') and len(line) > 10:
                title = line.strip()[:60]
                return title
        
        # 方法3：从URL中提取
        # 去掉https://，取最后一部分
        url_part = url.split('/')[-1].replace('-', ' ').replace('_', ' ')
        # 移除多余的数字和乱码
        url_part = re.sub(r'[0-9]+', '', url_part).strip()
        if url_part and len(url_part) > 5:
            return url_part[:40]
        
        # 最后备用
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
                # 提取标题
                title = self.extract_title_from_html(result.markdown, url)
                
                # 提取内容（取前4000字）
                content = result.markdown[:4000]
                
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
