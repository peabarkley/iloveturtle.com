#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为英文站所有页面补 hreflang。
规则：
- 在 <link rel="canonical" ...> 后插入三行 hreflang
- 英文页 → en: 自己, zh-Hant: 对应中文页, x-default: 自己
"""

import re
from pathlib import Path

# 英文页 → 中文页 URL 映射
# 如果中文页 URL 和英文页相同（只是加了 /zh 前缀），直接用规则生成
# 特殊映射（路径不一致的）单独列出
SPECIAL_MAP = {
    # 英文 URL 路径 → 中文 URL 路径
    "/article/turtle-vocal-cords.html": "/zh/article/turtle-vocal-cords.html",
    "/article/turtle-shell-anatomy.html": "/zh/article/turtle-shell-anatomy.html",
    "/article/can-turtles-hear.html": "/zh/article/can-turtles-hear.html",
    "/article/turtle-communication.html": "/zh/article/turtle-communication.html",
    "/article/cloacal-respiration.html": "/zh/article/cloacal-respiration.html",
    "/article/turtle-shell-pain.html": "/zh/article/turtle-shell-pain.html",
    "/article/best-pet-turtle-beginners.html": "/zh/article/best-pet-turtle-beginners.html",
    "/article/red-eared-slider-care.html": "/zh/article/red-eared-slider-care.html",
    "/article/musk-turtle-care.html": "/zh/article/musk-turtle-care.html",
    "/article/sulcata-vs-hermann.html": "/zh/article/sulcata-vs-hermann.html",
    "/article/small-turtles-stay-small.html": "/zh/article/small-turtles-stay-small.html",
    "/article/what-do-turtles-eat.html": "/zh/article/what-do-turtles-eat.html",
    "/article/turtle-hibernation-guide.html": "/zh/article/turtle-hibernation-guide.html",
    "/article/correct-water-temperature.html": "/zh/article/correct-water-temperature.html",
    "/article/how-to-hold-a-turtle.html": "/zh/article/how-to-hold-a-turtle.html",
    "/article/turtle-respiratory-infection.html": "/zh/article/turtle-respiratory-infection.html",
    "/article/shell-rot-treatment.html": "/zh/article/shell-rot-treatment.html",
    "/article/turtle-eye-infection.html": "/zh/article/turtle-eye-infection.html",
    "/article/metabolic-bone-disease.html": "/zh/article/meta-...nic-bone-disease.html",
    "/article/signs-sick-turtle.html": "/zh/article/signs-sick-turtle.html",
    "/article/turtle-tank-setup-beginners.html": "/zh/article/turtle-tank-setup-beginners.html",
    "/article/do-turtles-need-uvb.html": "/zh/article/do-turtles-need-uvb.html",
    "/article/best-turtle-filter.html": "/zh/article/best-turtle-filter.html",
    "/article/turtle-basking-platform.html": "/zh/article/turtle-basking-platform.html",
    "/article/turtle-safe-aquascaping.html": "/zh/article/turtle-safe-aquascaping.html",
    "/article/outdoor-turtle-pond.html": "/zh/article/outdoor-turtle-pond.html",
    # 分类页
    "/category/species.html": "/zh/category/species.html",
    "/category/care.html": "/zh/category/care.html",
    "/category/health.html": "/zh/category/health.html",
    "/category/setup.html": "/zh/category/setup.html",
    "/category/facts.html": "/zh/category/facts.html",
    # 列表页
    "/article-list.html": "/zh/article-list.html",
    # 核心页
    "/about.html": "/zh/about.html",
    "/contact.html": "/zh/contact.html",
    "/privacy.html": "/zh/privacy.html",
    "/disclaimer.html": "/zh/disclaimer.html",
    "/terms.html": "/zh/terms.html",
    # 首页
    "/": "/zh/",
}


def get_zh_url(en_path):
    """根据英文路径获取中文路径"""
    if en_path in SPECIAL_MAP:
        return SPECIAL_MAP[en_path]
    # 默认规则：/article/xxx.html → /zh/article/xxx.html
    if en_path.startswith("/"):
        return "/zh" + en_path
    return "/zh/" + en_path


def fix_file(filepath):
    """修复单个文件的 hreflang"""
    content = filepath.read_text(encoding="utf-8")

    # 推断英文路径
    rel = filepath.relative_to(Path("."))
    if str(rel) == "index.html":
        en_path = "/"
    else:
        en_path = "/" + str(rel).replace("\\", "/")

    zh_path = get_zh_url(en_path)

    # 检查是否已有 hreflang（避免重复插入）
    if 'hreflang="en"' in content:
        return False  # 已有，跳过

    # 构造三行 hreflang（英文页视角）
    hreflang_block = f'''<link rel="alternate" hreflang="en" href="https://www.iloveturtle.com{en_path}">
<link rel="alternate" hreflang="zh-Hant" href="https://www.iloveturtle.com{zh_path}">
<link rel="alternate" hreflang="x-default" href="https://www.iloveturtle.com{en_path}">'''

    # 在 <link rel="canonical" ...> 后插入
    canonical_pattern = r'(<link rel="canonical"[^>]*>)'
    if re.search(canonical_pattern, content):
        content = re.sub(
            canonical_pattern,
            r'\1\n' + hreflang_block,
            content,
            count=1
        )
    else:
        # 没有 canonical，在 </title> 后插入
        content = re.sub(
            r'(</title>)',
            r'\1\n' + hreflang_block,
            content,
            count=1
        )

    filepath.write_text(content, encoding="utf-8")
    return True


# 执行
changed = 0
skipped = 0
for path in Path(".").rglob("*.html"):
    if ".git" in path.parts or "zh" in path.parts:
        continue
    if fix_file(path):
        print(f"✅ {path}")
        changed += 1
    else:
        print(f"⏭️  {path}  (已有 hreflang，跳过)")
        skipped += 1

print()
print(f"完成：修复 {changed} 个文件，跳过 {skipped} 个。")