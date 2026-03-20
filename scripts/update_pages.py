#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
from pathlib import Path

class PageUpdater:
    def __init__(self):
        self.root_dir = Path("..")  # 回到项目根目录
        self.article_dir = self.root_dir / "zh" / "article"
        self.category_dir = self.root_dir / "zh" / "category"
        
    def get_latest_articles(self, count=10):
        """获取最新的10篇文章"""
        articles = []
        if not self.article_dir.exists():
            return articles
            
        for file in sorted(self.article_dir.glob("*.zh.html"), reverse=True)[:count]:
            # 从文件中读取标题
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取标题
                title_match = re.search(r'<h1>(.*?)</h1>', content)
                if title_match:
                    title = title_match.group(1)
                else:
                    title = file.stem.replace('.zh', '').replace('-', ' ')
                
                # 提取分类
                category_match = re.search(r'分类：.*?>(.*?)</a>', content)
                category = category_match.group(1) if category_match else "其他"
                
                articles.append({
                    'file': file.name,
                    'title': title,
                    'category': category,
                    'date': file.stem[:8]  # 文件名前8位是日期
                })
        
        return articles
    
    def update_category_page(self, category_name, articles):
        """更新分类页面"""
        category_file = self.category_dir / f"{category_name}.html"
        if not category_file.exists():
            print(f"  ⚠️ 分类页面不存在: {category_name}")
            return
        
        with open(category_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到文章列表区域
        list_pattern = r'(<div class="article-list">.*?</div>\s*</div>\s*<!-- 文章列表结束 -->)'
        
        # 生成新的文章列表HTML
        new_list = '<div class="article-list">\n'
        for article in articles[:8]:  # 显示前8篇
            new_list += f'''
            <div class="list-item">
                <h2><a href="../article/{article['file']}">{article['title']}</a></h2>
                <div class="list-meta">
                    <span><i class="far fa-calendar-alt"></i> {article['date'][:4]}-{article['date'][4:6]}-{article['date'][6:8]}</span>
                    <span><i class="far fa-eye"></i> 最新</span>
                </div>
                <p class="list-excerpt">来自 {article['category']} 分类的最新文章</p>
                <a href="../article/{article['file']}" class="read-more-btn">阅读全文</a>
            </div>
            '''
        new_list += '</div>\n</div><!-- 文章列表结束 -->'
        
        # 替换
        if re.search(list_pattern, content, re.DOTALL):
            new_content = re.sub(list_pattern, new_list, content, flags=re.DOTALL)
            with open(category_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ 已更新: {category_name}")
    
    def update_homepage(self, articles):
        """更新首页"""
        homepage = self.root_dir / "zh" / "index.html"
        if not homepage.exists():
            homepage = self.root_dir / "index.html"
        
        with open(homepage, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到最新文章区域
        pattern = r'(<div class="latest-posts">.*?<ul>)(.*?)(</ul>.*?</div>)'
        
        # 生成新的文章列表
        new_list = ''
        for article in articles[:5]:  # 首页显示前5篇
            new_list += f'''
                <li><a href="zh/article/{article['file']}">{article['title']}</a> <span class="date">[{article['date'][:4]}-{article['date'][4:6]}]</span></li>'''
        
        # 替换
        match = re.search(pattern, content, re.DOTALL)
        if match:
            new_content = content.replace(match.group(2), new_list)
            with open(homepage, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  ✅ 已更新首页")
    
    def run(self):
        """执行更新"""
        print(f"\n{'='*50}")
        print(f"开始更新页面: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # 获取最新文章
        articles = self.get_latest_articles(20)
        if not articles:
            print("❌ 没有找到文章")
            return
        
        print(f"📚 找到 {len(articles)} 篇最新文章")
        
        # 按分类分组
        categories = {}
        for article in articles:
            cat = article['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        # 更新首页
        self.update_homepage(articles)
        
        # 更新各个分类页面
        for cat_name, cat_articles in categories.items():
            # 将中文分类名转为文件名
            cat_map = {
                "颠覆认知": "facts-disruption",
                "神奇生理": "facts-physiology", 
                "新手避坑": "facts-beginner",
                "陆龟": "species-tortoise",
                "水龟": "species-water",
                "半水栖龟": "species-semiaquatic",
                "饲养要点": "care-essentials",
                "造景生态": "care-aquascape",
                "季节提醒": "care-seasonal",
                "疾病防治": "disease-treatment",
                "专家推荐": "disease-expert"
            }
            
            file_name = cat_map.get(cat_name, cat_name)
            self.update_category_page(file_name, cat_articles)
        
        print(f"\n{'='*50}")
        print(f"✅ 页面更新完成！")
        print(f"{'='*50}")

if __name__ == "__main__":
    updater = PageUpdater()
    updater.run()
