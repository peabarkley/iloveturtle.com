#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

# 映射表：每篇文章对应的 3 篇相关文章
RELATED_MAP = {
    # 疾病类
    "turtle-respiratory-infection": [
        ("/zh/article/turtle-eye-infection.html", "烏龜白眼病怎麼治？"),
        ("/zh/article/shell-rot-treatment.html", "烏龜腐皮怎麼治？"),
        ("/zh/article/signs-sick-turtle.html", "烏龜生病的 10 個信號")
    ],
    "turtle-eye-infection": [
        ("/zh/article/turtle-respiratory-infection.html", "烏龜肺炎怎麼治？"),
        ("/zh/article/snapping-turtle-white-eye-disease.html", "鱷龜白眼病：症狀與治療"),
        ("/zh/article/signs-sick-turtle.html", "烏龜生病的 10 個信號")
    ],
    # 品种类
    "musk-turtle-care": [
        ("/zh/article/best-turtle-food.html", "烏龜飼料怎麼選？"),
        ("/zh/article/small-turtles-stay-small.html", "小型龜推薦"),
        ("/zh/article/tortoise2.html", "紅腿陸龜飼養指南")
    ],
    "tortoise2": [
        ("/zh/article/best-turtle-food.html", "烏龜飼料怎麼選？"),
        ("/zh/article/sulcata-vs-hermann.html", "蘇卡達 vs 赫曼陸龜"),
        ("/zh/article/musk-turtle-care.html", "麝香龜飼養指南")
    ],
    "best-turtle-food": [
        ("/zh/article/what-do-turtles-eat.html", "烏龜吃什麼？完整飲食指南"),
        ("/zh/article/musk-turtle-care.html", "麝香龜飼養指南"),
        ("/zh/article/tortoise2.html", "紅腿陸龜飼養指南")
    ],
    # 科普类
    "turtle-physiology3": [
        ("/zh/article/turtle-vision-color.html", "烏龜看得到顏色嗎？"),
        ("/zh/article/can-turtles-hear.html", "烏龜聽得到聲音嗎？"),
        ("/zh/article/turtle-shell-anatomy.html", "龜殼解剖完整解說")
    ],
    "turtle-vision-color": [
        ("/zh/article/turtle-physiology3.html", "烏龜視力好嗎？完整解析"),
        ("/zh/article/turtle-shell-anatomy.html", "龜殼解剖完整解說"),
        ("/zh/article/can-turtles-hear.html", "烏龜聽得到聲音嗎？")
    ],
    "can-turtles-hear": [
        ("/zh/article/turtle-physiology3.html", "烏龜視力好嗎？完整解析"),
        ("/zh/article/turtle-communication.html", "烏龜怎麼交流？"),
        ("/zh/article/cloacal-respiration.html", "烏龜用屁股呼吸？")
    ],
}

# 默认推荐（如果文章不在上面的映射里）
DEFAULT_LINKS = [
    ("/zh/article/what-do-turtles-eat.html", "烏龜吃什麼？完整飲食指南"),
    ("/zh/article/turtle-tank-setup-beginners.html", "龜缸搭建完整指南"),
    ("/zh/article/signs-sick-turtle.html", "烏龜生病的 10 個信號")
]

HTML_TEMPLATE = """
        <!-- 相關文章模塊 -->
        <div class="related-posts-section" style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2eed6;">
            <h3 style="color: #1f4a1f; font-size: 1.2rem; margin-bottom: 16px;"><i class="fas fa-link"></i> 相關文章</h3>
            <ul style="list-style: none; padding: 0; display: grid; grid-template-columns: 1fr; gap: 12px;">
                {links}
            </ul>
        </div>
"""

LINK_TEMPLATE = '<li><a href="{url}" style="color: #2c7a2c; text-decoration: none;">{title}</a></li>'

def process_file(file_path):
    slug = file_path.stem
    html = file_path.read_text(encoding='utf-8')
    
    # 如果已经有相关文章模块，跳过
    if 'related-posts-section' in html:
        return False
        
    # 获取相关文章列表
    related = RELATED_MAP.get(slug, DEFAULT_LINKS)
    links_html = "\n".join([LINK_TEMPLATE.format(url=url, title=title) for url, title in related])
    block = HTML_TEMPLATE.format(links=links_html)
    
    # 插入到 </article> 之前
    if '</article>' in html:
        html = html.replace('</article>', block + '\n</article>', 1)
        file_path.write_text(html, encoding='utf-8')
        print(f"[OK] 已为 {file_path.name} 添加相关文章")
        return True
    return False

def main():
    zh_dir = Path("zh/article")
    if not zh_dir.exists():
        print("找不到 zh/article 目录")
        return
        
    changed = 0
    for f in zh_dir.glob("*.html"):
        if process_file(f):
            changed += 1
            
    print(f"\n完成！共修改了 {changed} 个文件。")

if __name__ == "__main__":
    main()
