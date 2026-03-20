#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

def update_homepage():
    root_dir = Path("..")
    homepage = root_dir / "index.html"
    
    if not homepage.exists():
        print("❌ 首页文件不存在")
        return
    
    with open(homepage, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在页脚前添加文章列表链接
    new_content = content.replace(
        '</footer>',
        '''
    <div style="text-align: center; margin: 20px 0; padding: 10px;">
        <a href="/zh/articles.html" style="background: #2b532b; color: white; padding: 12px 30px; border-radius: 40px; text-decoration: none; font-weight: 600;">📚 查看所有文章列表</a>
    </div>
</footer>'''
    )
    
    with open(homepage, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ 首页已更新")

if __name__ == "__main__":
    update_homepage()
