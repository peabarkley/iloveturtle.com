#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

GA4_CODE = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-EH6JN5YR4Z"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-EH6JN5YR4Z');
    </script>
"""

def process_file(file_path):
    html = file_path.read_text(encoding='utf-8')
    
    # 如果已经有 GA4 代码，跳过
    if 'G-EH6JN5YR4Z' in html:
        return False
        
    # 找到 <head> 标签（忽略大小写）
    match = re.search(r'(<head[^>]*>)', html, re.IGNORECASE)
    if match:
        head_tag = match.group(1)
        # 将 GA4 代码插在 <head> 标签的下一行
        html = html.replace(head_tag, head_tag + GA4_CODE, 1)
        file_path.write_text(html, encoding='utf-8')
        print(f"[OK] 已为 {file_path.name} 插入 GA4 代码")
        return True
    
    print(f"[SKIP] {file_path.name} 找不到 <head> 标签")
    return False

def main():
    # 扫描根目录、article 文件夹、zh 文件夹和 zh/article 文件夹
    dirs_to_scan = [Path("."), Path("article"), Path("zh"), Path("zh/article")]
    
    changed = 0
    for d in dirs_to_scan:
        if not d.exists():
            continue
        # 只扫描 html 文件，排除模板文件
        for f in d.glob("*.html"):
            if "template" in f.name:
                continue
            if process_file(f):
                changed += 1
                
    print(f"\n完成！共修改了 {changed} 个文件。")

if __name__ == "__main__":
    main()
