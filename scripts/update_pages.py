#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from pathlib import Path

class PageUpdater:
    def __init__(self):
        self.root_dir = Path("..")
        self.article_dir = self.root_dir / "zh" / "article"
        
    def run(self):
        """只创建文章列表，不修改分类页面"""
        print(f"\n{'='*50}")
        print(f"开始更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # 检查文章目录
        if not self.article_dir.exists():
            print(f"📁 创建文章目录: {self.article_dir}")
            self.article_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有文章
        articles = []
        for file in sorted(self.article_dir.glob("*.zh.html"), reverse=True):
            articles.append(file.name)
            print(f"📄 找到文章: {file.name}")
        
        if not articles:
            print("📝 当前没有文章")
            return
        
        print(f"\n✅ 完成！共有 {len(articles)} 篇文章")
        print(f"📁 文章目录: zh/article/")

if __name__ == "__main__":
    updater = PageUpdater()
    updater.run()
