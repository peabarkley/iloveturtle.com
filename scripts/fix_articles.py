#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path

def fix_articles():
    root_dir = Path("..")
    article_dir = root_dir / "zh" / "article"
    
    if not article_dir.exists():
        print("❌ 文章目录不存在")
        return
    
    articles = list(article_dir.glob("*.zh.html"))
    print(f"📊 找到 {len(articles)} 篇文章")
    
    for file in articles:
        print(f"\n📄 检查: {file.name}")
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查标题
        title_match = re.search(r'<h1>(.*?)</h1>', content)
        if title_match:
            print(f"   当前标题: {title_match.group(1)}")
        else:
            print(f"   ⚠️ 没有找到标题")

if __name__ == "__main__":
    fix_articles()
