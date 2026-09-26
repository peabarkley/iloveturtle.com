{\rtf1\ansi\ansicpg936\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset134 PingFangSC-Regular;\f2\fnil\fcharset0 LucidaGrande;
\f3\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/usr/bin/env python3\
# -*- coding: utf-8 -*-\
"""\

\f1 \'d0\'de\'b8\'b4\'d6\'d0\'ce\'c4\'d5\'be\'d2\'b3\'c3\'e6\'b5\'c4
\f0  hreflang
\f1 \'a3\'ba
\f0 \
1. 
\f1 \'b0\'d1
\f0  hreflang="zh-Hans" 
\f1 \'b8\'c4\'b3\'c9
\f0  "zh-Hant"\
2. 
\f1 \'b2\'b9\'c9\'cf\'c8\'b1\'b5\'c4
\f0  hreflang="en"\
3. 
\f1 \'b0\'d1
\f0  x-default 
\f1 \'b4\'d3\'a1\'b8\'d6\'b8\'d7\'d4\'bc\'ba\'a1\'b9\'b8\'c4\'b3\'c9\'a1\'b8\'d6\'b8\'d3\'a2\'ce\'c4\'d2\'b3\'a1\'b9
\f0 \
"""\
\
import re\
from pathlib import Path\
\
# 
\f1 \'d6\'d0\'ce\'c4\'c2\'b7\'be\'b6
\f0  
\f2 \uc0\u8594 
\f0  
\f1 \'d3\'a2\'ce\'c4\'c2\'b7\'be\'b6
\f0  
\f1 \'b7\'b4\'cf\'f2\'d3\'b3\'c9\'e4
\f0 \
REVERSE_MAP = \{\
    "/zh/": "/",\
    "/zh/article-list.html": "/article-list.html",\
    "/zh/about.html": "/about.html",\
    "/zh/contact.html": "/contact.html",\
    "/zh/privacy.html": "/privacy.html",\
    "/zh/disclaimer.html": "/disclaimer.html",\
    "/zh/terms.html": "/terms.html",\
    "/zh/category/species.html": "/category/species.html",\
    "/zh/category/care.html": "/category/care.html",\
    "/zh/category/health.html": "/category/health.html",\
    "/zh/category/setup.html": "/category/setup.html",\
    "/zh/category/facts.html": "/category/facts.html",\
\}\
\
\
def get_en_url(zh_path):\
    """
\f1 \'b8\'f9\'be\'dd\'d6\'d0\'ce\'c4\'c2\'b7\'be\'b6\'bb\'f1\'c8\'a1\'d3\'a2\'ce\'c4\'c2\'b7\'be\'b6
\f0 """\
    if zh_path in REVERSE_MAP:\
        return REVERSE_MAP[zh_path]\
    # 
\f1 \'c4\'ac\'c8\'cf\'b9\'e6\'d4\'f2\'a3\'ba
\f0 /zh/article/xxx.html 
\f2 \uc0\u8594 
\f0  /article/xxx.html\
    if zh_path.startswith("/zh/"):\
        return zh_path[3:]  # 
\f1 \'c8\'a5\'b5\'f4
\f0  /zh\
    return "/"\
\
\
def fix_file(filepath):\
    """
\f1 \'d0\'de\'b8\'b4\'b5\'a5\'b8\'f6\'d6\'d0\'ce\'c4\'d2\'b3
\f0 """\
    content = filepath.read_text(encoding="utf-8")\
\
    # 
\f1 \'cd\'c6\'b6\'cf\'d6\'d0\'ce\'c4\'c2\'b7\'be\'b6
\f0 \
    rel = filepath.relative_to(Path("."))\
    zh_path = "/" + str(rel).replace("\\\\", "/")\
    en_path = get_en_url(zh_path)\
\
    # 1. 
\f1 \'b0\'d1
\f0  zh-Hans 
\f1 \'b8\'c4\'b3\'c9
\f0  zh-Hant\
    content = content.replace('hreflang="zh-Hans"', 'hreflang="zh-Hant"')\
\
    # 2. 
\f1 \'bc\'ec\'b2\'e9\'b2\'a2\'b2\'b9
\f0  en
\f1 \'a3\'a8\'c8\'e7\'b9\'fb\'c3\'bb\'d3\'d0\'a3\'a9
\f0 \
    if 'hreflang="en"' not in content:\
        # 
\f1 \'d4\'da
\f0  canonical 
\f1 \'ba\'f3\'b2\'e5\'c8\'eb
\f0  en 
\f1 \'ba\'cd\'d0\'de\'d5\'fd
\f0  x-default\
        # 
\f1 \'cf\'c8\'d5\'d2
\f0  canonical 
\f1 \'d0\'d0
\f0 \
        canonical_match = re.search(r'<link rel="canonical"[^>]*>', content)\
        if canonical_match:\
            canonical_line = canonical_match.group(0)\
            # 
\f1 \'b9\'b9\'d4\'ec\'cd\'ea\'d5\'fb\'c8\'fd\'d0\'d0
\f0 \
            new_block = f'''\{canonical_line\}\
<link rel="alternate" hreflang="en" href="https://www.iloveturtle.com\{en_path\}">\
<link rel="alternate" hreflang="zh-Hant" href="https://www.iloveturtle.com\{zh_path\}">\
<link rel="alternate" hreflang="x-default" href="https://www.iloveturtle.com\{en_path\}">'''\
            # 
\f1 \'cc\'e6\'bb\'bb\'d4\'ad\'d3\'d0\'b5\'c4
\f0  canonical + 
\f1 \'cb\'f9\'d3\'d0
\f0  hreflang 
\f1 \'d0\'d0
\f0 \
            # 
\f1 \'c6\'a5\'c5\'e4
\f0  canonical 
\f1 \'d2\'d4\'bc\'b0\'ba\'f3\'c3\'e6\'b5\'c4\'c8\'f4\'b8\'c9
\f0  hreflang\
            pattern = r'(<link rel="canonical"[^>]*>)(\\s*<link rel="alternate"[^>]*>)*'\
            content = re.sub(pattern, new_block, content, count=1)\
\
    # 3. 
\f1 \'d0\'de\'d5\'fd
\f0  x-default 
\f1 \'d6\'b8\'cf\'f2\'a3\'a8\'c8\'e7\'b9\'fb\'d6\'b8\'cf\'f2\'d7\'d4\'bc\'ba\'a3\'a9
\f0 \
    content = re.sub(\
        r'<link rel="alternate" hreflang="x-default" href="https://www\\.iloveturtle\\.com/zh/[^"]*">',\
        f'<link rel="alternate" hreflang="x-default" href="https://www.iloveturtle.com\{en_path\}">',\
        content\
    )\
\
    filepath.write_text(content, encoding="utf-8")\
    return True\
\
\
# 
\f1 \'d6\'b4\'d0\'d0
\f0 \
changed = 0\
for path in Path(".").rglob("*.html"):\
    if ".git" in path.parts:\
        continue\
    if not str(path).startswith("zh"):\
        continue\
    if fix_file(path):\
        print(f"
\f3 \uc0\u9989 
\f0  \{path\}")\
        changed += 1\
\
print()\
print(f"
\f1 \'cd\'ea\'b3\'c9\'a3\'ba\'d0\'de\'b8\'b4
\f0  \{changed\} 
\f1 \'b8\'f6\'d6\'d0\'ce\'c4\'d2\'b3\'a1\'a3
\f0 ")}