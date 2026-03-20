#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

def add_entry():
    root_dir = Path("..")
    homepage = root_dir / "index.html"
    
    if not homepage.exists():
        print("❌ 首页不存在")
        return
    
    with open(homepage, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在欢迎区域后添加文章列表入口
    entry_html = '''
    <div style="text-align: center; margin: 30px 0;">
        <a href="/zh/articles.html" style="display: inline-block; background: #2b532b; color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-size: 1.2rem; font-weight: bold;">
            📚 查看所有文章（共9篇）
        </a>
    </div>
'''
    
    # 在欢迎区域后插入
    new_content = content.replace('</section>', '</section>' + entry_html)
    
    with open(homepage, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 首页已添加文章列表入口")

if __name__ == "__main__":
    add_entry()
