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
            '违法和不良信息举报电话', '网上有害信息举报', '涉未成年人举报',
            '热门', '推荐', '最新', '视频', '图文', '专栏', '动态',
            '关注的人', '粉丝数', '获赞数', '播放数', '弹幕数',
            'www', 'http', 'https', '.com', '.cn', '.net'
        ]
        
        # 标题黑名单（不能作为标题的词）
        self.bad_titles = [
            '首页', '搜索', '知乎', 'B站', '哔哩哔哩', '贴吧', '百度',
            'Google', 'bing', '搜索', '结果', '列表', '下一页',
            '登录', '注册', '忘记密码', '立即下载', '打开APP',
            '热门视频', '推荐视频', '最新视频', '相关视频',
            '评论', '点赞', '收藏', '转发', '分享'
        ]
        
        # 乌龟相关关键词
        self.turtle_keywords = [
            '乌龟', '养龟', '巴西龟', '陆龟', '水龟', '蛋龟', '麝香', 
            '剃刀', '窄桥', '草龟', '花龟', '黄缘', '闭壳龟', '苏卡达',
            '赫曼', '红腿', '豹龟', '辐射', '缅陆', '鳄龟', '枫叶龟',
            '锯缘', '安布', '木纹龟', '冬眠', '龟缸', '造景', '过滤',
            'UVB', '晒背', '腐皮', '肺炎', '白眼病', '软壳', '浮水',
            '加热', '温度', '水质', '喂食', '龟粮', '活食', '蚯蚓',
            'turtle', 'tortoise', 'slider', 'musk', 'sulcata', 'hermann',
            '孵化', '繁殖', '蛋', '幼苗', '幼龟', '成龟', '公母',
            '品种', '品相', '发色', '生长纹', '隆背', '真菌'
        ]
    
    def is_valid_title(self, title):
        """检查标题是否有效"""
        if not title or len(title) < 4 or len(title) > 50:
            return False
        # 检查黑名单
        if any(bad in title for bad in self.bad_titles):
            return False
        # 检查是否全是符号或数字
        if re.match(r'^[\W\d_]+$', title):
            return False
        # 应该包含至少一个中文字符
        if not re.search(r'[\u4e00-\u9fff]', title):
            return False
        return True
    
    def clean_content(self, text):
        """清理内容，去除导航菜单等无关内容"""
        lines = text.split('\n')
        cleaned_lines = []
        turtle_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
                
            # 跳过太短的行
            if len(line) < 8:
                continue
                
            # 跳过太长的行（可能是代码）
            if len(line) > 200:
                continue
                
            # 跳过包含导航关键词的行
            if any(kw in line for kw in self.nav_keywords):
                continue
                
            # 跳过URL行
            if re.match(r'^https?://', line) or '.com' in line or '.cn' in line:
                continue
                
            # 跳过包含太多符号的行
            if line.count('{') > 2 or line.count('}') > 2 or line.count('*') > 3:
                continue
                
            # 跳过全是数字和符号的行
            if re.match(r'^[\d\s\-_+=*&^%$#@!~`|\\/\[\]{}()<>]+$', line):
                continue
                
            # 检查是否包含中文字符
            if re.search(r'[\u4e00-\u9fff]', line):
                # 记录乌龟相关内容
                if any(kw in line for kw in self.turtle_keywords):
                    turtle_lines.append(line)
                cleaned_lines.append(line)
        
        # 优先返回乌龟相关内容
        if len(turtle_lines) >= 2:
            return '\n\n'.join(turtle_lines[:20])
        elif len(cleaned_lines) >= 3:
            return '\n\n'.join(cleaned_lines[:20])
        else:
            return ""
    
    def extract_title(self, url, content):
        """从内容中提取标题 - 最终优化版"""
        lines = content.split('\n')
        
        # 第一步：找包含乌龟关键词的行
        for line in lines[:30]:
            line = line.strip()
            # 长度过滤
            if len(line) < 6 or len(line) > 50:
                continue
            # 黑名单过滤
            if any(bad in line for bad in self.bad_titles):
                continue
            # 如果包含乌龟关键词
            if any(kw in line for kw in self.turtle_keywords):
                # 清理多余符号
                clean = re.sub(r'^[#\s*【】\[\]「」_\-、，。！？…\s]+', '', line)
                clean = re.sub(r'[#\s*【】\[\]「」_\-、，。！？…\s]+$', '', clean)
                if self.is_valid_title(clean):
                    return clean
        
        # 第二步：找第一个有意义的中文行
        for line in lines[:20]:
            line = line.strip()
            if len(line) < 8 or len(line) > 50:
                continue
            if any(bad in line for bad in self.bad_titles):
                continue
            if re.search(r'[\u4e00-\u9fff]', line):
                clean = re.sub(r'^[#\s*【】\[\]「」_\-]+', '', line)
                if self.is_valid_title(clean):
                    return clean
        
        # 第三步：从URL中提取有意义的部分
        if 'zhuanlan.zhihu.com' in url:
            return "知乎乌龟科普"
        elif 'bilibili.com' in url:
            if 'video' in url:
                return "B站乌龟视频"
            else:
                return "B站乌龟专栏"
        elif 'tieba.baidu.com' in url:
            return "贴吧乌龟讨论"
        elif 'cnki' in url or 'baidu' in url:
            return "乌龟资料"
        else:
            # 从当前时间生成一个简单的标题
            now = datetime.now()
            return f"乌龟科普{now.month}月{now.day}日"
    
    def is_turtle_related(self, text):
        """检查内容是否与乌龟相关"""
        if not text:
            return False
        text_lower = text.lower()
        # 至少需要匹配到2个乌龟关键词
        match_count = 0
        for kw in self.turtle_keywords:
            if kw.lower() in text_lower:
                match_count += 1
                if match_count >= 2:
                    return True
        return match_count >= 1
    
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
                
                if len(cleaned_content) < 150:
                    print(f"    内容过短({len(cleaned_content)}字符)，跳过")
                    return None
                
                # 提取标题
                title = self.extract_title(url, cleaned_content)
                
                print(f"    找到标题: {title}")
                print(f"    内容长度: {len(cleaned_content)} 字符")
                
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
        
        # 移除特殊字符，只保留字母数字中文和空格
        clean_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)
        # 转小写，空格变中划线
        slug = clean_title.lower().strip().replace(' ', '-')
        # 限制长度
        slug = slug[:40]
        
        # 如果slug为空，用时间戳
        if not slug or len(slug) < 4:
            import time
            slug = f"article-{int(time.time())}"
        
        return f"{date}-{slug}"
    
    async def run(self):
        """运行采集器"""
        print(f"\n{'='*50}")
        print(f"开始采集: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        article_count = 0
        success_count = 0
        fail_count = 0
        
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
        )
        
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for source_name, source_config in SOURCES.items():
                    if article_count >= self.max_articles_per_run:
                        break
                        
                    print(f"\n📡 正在采集 {source_name}...")
                    
                    urls = source_config.get("urls", [])
                    for url in urls:
                        if article_count >= self.max_articles_per_run:
                            break
                            
                        print(f"\n  🔗 访问: {url}")
                        
                        # 随机延迟，避免被封
                        delay = random.uniform(3, 6)
                        print(f"     等待 {delay:.1f} 秒...")
                        await asyncio.sleep(delay)
                        
                        data = await self.scrape_url(crawler, url, source_name)
                        
                        if data and data.get("content") and len(data["content"]) > 200:
                            # 检查重复
                            if self.deduplicator.is_duplicate(data["title"], data["content"]):
                                print(f"  ⏭️ 文章已存在，跳过")
                                fail_count += 1
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
                            success_count += 1
                            print(f"  ✅ 已保存 ({article_count}/{self.max_articles_per_run})")
                        else:
                            print(f"  ⚠️ 内容无效，跳过")
                            fail_count += 1
        
        except Exception as e:
            print(f"❌ 采集过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*50}")
        print(f"采集完成！")
        print(f"✅ 成功: {success_count} 篇")
        print(f"❌ 失败: {fail_count} 篇")
        print(f"📁 文件保存在: {self.output_dir.absolute()}")
        print(f"{'='*50}")

async def main():
    scraper = AutoScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
