#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动为文章正文添加内链脚本
- 只替换正文中第一次出现的指定关键词
- 跳过已有的 <a> 标签内的文本
- 跳过标题（<h1>~<h6>）内的文本
"""

import re
from pathlib import Path

# ==========================================
# 1. 配置区：关键词到目标 URL 的映射
# ==========================================
LINK_MAP = {
    # 高优先级：推排名的核心词
    "麝香龜": "/zh/article/musk-turtle-care.html",
    "麝香龟": "/zh/article/musk-turtle-care.html",
    
    # 高 CTR：疾病类问句
    "烏龜肺炎": "/zh/article/turtle-respiratory-infection.html",
    "烏龜白眼病": "/zh/article/turtle-eye-infection.html",
    "鱷龜白眼病": "/zh/article/snapping-turtle-white-eye-disease.html",
    
    # 视力族
    "烏龜視力": "/zh/article/turtle-physiology3.html",
    "烏龜看得到顏色嗎": "/zh/article/turtle-physiology3.html",
    
    # 品种与饲养
    "紅腿陸龜": "/zh/article/tortoise2.html",
    "巴西龜": "/zh/article/red-eared-slider-care.html",
    "迷你龜": "/zh/article/small-turtles-stay-small.html",
    "長不大的烏龜": "/zh/article/small-turtles-stay-small.html",
    
    # 设备与造景
    "龜缸過濾器": "/zh/article/best-turtle-filter.html",
    "UVB 燈": "/zh/article/do-turtles-need-uvb.html",
    "曬台": "/zh/article/turtle-basking-platform.html",
}

# 需要扫描的目录（如果想加上英文文章，可以把 'article' 也加进去）
TARGET_DIRS = ["zh/article"]

# ==========================================
# 2. 核心逻辑
# ==========================================

def remove_html_tags(html):
    """用于简单去除标签，防止破坏结构，这里主要用来保护已有链接和标题"""
    return re.sub(r'<[^>]+>', '', html)

def add_links_to_html(html, current_slug):
    """
    为 HTML 正文添加内链。
    只替换 <div class="article-content"> 到 </div> 之间的内容。
    """
    # 提取正文部分，防止把导航栏、侧边栏的词汇也加了链接
    content_match = re.search(r'<div class="article-content">(.*?)</div>', html, re.DOTALL)
    if not content_match:
        return html
    
    content = content_match.group(1)
    
    for keyword, target_url in LINK_MAP.items():
        # 如果链接指向当前页面自身，跳过（避免自己链自己）
        if target_url.endswith(f"{current_slug}.html"):
            continue
            
        # 构造正则：匹配关键词，但要求它不在 <a> 标签内部，且不在 HTML 标签属性里
        # 这是一个简化版的正向断言，确保关键词前面没有 href="..." 等属性
        # 为了防止误伤标题，我们先暂时把标题替换成占位符
        protected_content = re.sub(r'(<h[1-6][^>]*>.*?</h[1-6]>)', r'###PROTECTED###', content, flags=re.DOTALL)
        
        # 在非链接、非保护区域的文本中查找关键词
        # 匹配规则：不在 <a ...>...</a> 内部
        pattern = re.compile(r'(?<!<a[^>]*>)(' + re.escape(keyword) + r')(?!</a>)')
        
        # 执行替换，最多替换 1 次（count=1）
        new_protected_content, num_subs = pattern.subn(
            rf'<a href="{target_url}">\1</a>', 
            protected_content, 
            count=1
        )
        
        if num_subs > 0:
            # 如果成功替换，恢复被保护的标题
            protected_content = new_protected_content
            # 在控制台打印日志
            print(f"  [+] 在 {current_slug}.html 添加内链: {keyword} -> {target_url}")
            
        # 还原标题
        content = protected_content.replace('###PROTECTED###', '') # 这里其实丢失了原始标题内容，需要优化

    return html

# 修正版：更安全的正文替换逻辑，不损失原始 HTML
def safe_add_links(html, current_slug):
    content_match = re.search(r'(<div class="article-content">)(.*?)(</div>)', html, re.DOTALL)
    if not content_match:
        return html
    
    start_tag, content, end_tag = content_match.groups()
    original_content = content
    
    # 保护 <h1>~<h6> 和 <a> 标签内的内容
    def protect_tag(match):
        return f'<PROTECTED{hash(match.group(0))}>'
    
    # 保护所有标题
    content = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', protect_tag, content, flags=re.DOTALL)
    # 保护已有的链接
    content = re.sub(r'<a\s+[^>]*>.*?</a>', protect_tag, content, flags=re.DOTALL)
    
    # 开始替换
    for keyword, target_url in LINK_MAP.items():
        if target_url.endswith(f"{current_slug}.html"):
            continue
            
        # 匹配普通文本中的关键词
        # 简单起见，我们只找第一次出现的地方，把它变成链接
        pattern = re.compile(r'(?<![\w])(' + re.escape(keyword) + r')(?![\w])')
        
        def replace_func(m):
            return f'<a href="{target_url}">{m.group(1)}</a>'
            
        # 替换，count=1
        new_content, num_subs = pattern.subn(replace_func, content, count=1)
        
        if num_subs > 0:
            print(f"  [+] 在 {current_slug}.html 添加内链: {keyword} -> {target_url}")
            content = new_content

    # 还原被保护的内容
    def restore_tag(match):
        # 从原始内容里找对应的
        tag = match.group(0)
        hash_val = tag[len('<PROTECTED'):-1]
        return f'<ORIGINAL{hash_val}>' # 这里需要重新匹配，略复杂
    
    # 更简单的做法：反向替换
    # 因为 Python 正则不支持直接带回调的完美还原，我们用占位符列表
    return html

# ==========================================
# 3. 终极安全版本（推荐运行这个）
# ==========================================

def process_file(file_path, slug):
    html = file_path.read_text(encoding='utf-8')
    
    # 1. 提取正文
    content_match = re.search(r'(<div class="article-content">)(.*?)(\n\s*</div>\s*\n\s*(?:<div class="faq-section">|<footer class="article-footer">))', html, re.DOTALL)
    if not content_match:
        # 兼容不同的结结构，尝试简单的 div
        content_match = re.search(r'(<div class="article-content">)(.*?)(</div>)', html, re.DOTALL)
        if not content_match:
            return False
    
    start_tag = content_match.group(1)
    content = content_match.group(2)
    end_tag = content_match.group(3)
    
    # 2. 保护机制：用字典存被保护的标签
    protected_blocks = {}
    def protect(match):
        p_id = f"___PROTECT_{len(protected_blocks)}___"
        protected_blocks[p_id] = match.group(0)
        return p_id

    # 保护 <h> 标签和 <a> 标签
    temp_content = re.sub(r'<h[1-6][^>]*>.*?</h[1-6]>', protect, content, flags=re.DOTALL)
    temp_content = re.sub(r'<a\s+[^>]*>.*?</a>', protect, temp_content, flags=re.DOTALL)
    temp_content = re.sub(r'<blockquote.*?</blockquote>', protect, temp_content, flags=re.DOTALL)
    
    # 3. 执行替换
    changes = 0
    for keyword, target_url in LINK_MAP.items():
        if target_url.endswith(f"{slug}.html"):
            continue
            
        pattern = re.compile(r'(?<![\w])(' + re.escape(keyword) + r')(?![\w])')
        
        def replace_func(m):
            return f'<a href="{target_url}">{m.group(1)}</a>'
            
        temp_content, num_subs = pattern.subn(replace_func, temp_content, count=1)
        if num_subs > 0:
            print(f"  [+] 添加内链: {keyword} -> {target_url}")
            changes += 1

    # 4. 还原被保护的标签
    for p_id, original in protected_blocks.items():
        temp_content = temp_content.replace(p_id, original)
        
    if changes > 0:
        # 5. 拼装回原 HTML
        new_html = html.replace(start_tag + content + end_tag, start_tag + temp_content + end_tag)
        file_path.write_text(new_html, encoding='utf-8')
        return True
    
    return False

if __name__ == "__main__":
    print("开始扫描并添加内链...\n")
    total_changed = 0
    
    for target_dir in TARGET_DIRS:
        dir_path = Path(target_dir)
        if not dir_path.exists():
            continue
            
        for html_file in dir_path.glob("*.html"):
            slug = html_file.stem
            print(f"检查: {html_file.name}")
            if process_file(html_file, slug):
                total_changed += 1
                
    print(f"\n完成！共修改了 {total_changed} 个文件。")
