#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爱龟谷 - 自动文章生成与SEO优化脚本
功能：
1. 自动生成文章HTML
2. 自动添加Schema结构化数据
3. 自动生成/更新sitemap.xml
4. 自动通知Google更新
"""

import os
import re
import requests
from datetime import datetime
from pathlib import Path

# ==================== 配置区域 ====================
SITE_URL = "https://www.iloveturtle.com"
ARTICLE_DIR = "article"
IMAGE_DIR = "images"
SITEMAP_FILE = "sitemap.xml"

# ==================== Schema 相关函数 ====================

def add_schema_to_html(file_path, title, description, publish_date=None):
    """
    为单个HTML文件添加Schema标记
    
    Args:
        file_path: HTML文件路径
        title: 文章标题
        description: 文章描述
        publish_date: 发布日期（默认今天）
    
    Returns:
        bool: 是否成功
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有schema，避免重复添加
        if 'application/ld+json' in content:
            print(f"⏭️ 跳过（已有Schema）: {file_path}")
            return False
        
        # 设置日期
        if not publish_date:
            publish_date = datetime.now().strftime('%Y-%m-%d')
        
        # 创建schema JSON
        schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{description}",
  "author": {{
    "@type": "Person",
    "name": "爱龟谷"
  }},
  "datePublished": "{publish_date}",
  "dateModified": "{datetime.now().strftime('%Y-%m-%d')}"
}}
</script>'''
        
        # 在</head>标签前插入schema
        if '</head>' in content:
            content = content.replace('</head>', f'    {schema}\n</head>')
        else:
            # 如果没有head标签，添加完整的HTML结构
            content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    {schema}
</head>
<body>
{content}
</body>
</html>'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已添加Schema: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False


def generate_title_from_filename(filename):
    """从文件名生成标题（可自定义扩展）"""
    # 移除.html后缀
    name = filename.replace('.html', '').replace('.en', '')
    
    # 标题映射表（针对你的文章）
    title_map = {
        'musk-turtle': '麝香龟饲养指南 | 蛋龟入门必看',
        'hibernation': '乌龟冬眠全攻略 | 科学冬眠方法',
        'newbie-guide': '新手养龟避坑指南 | 入门必看',
        'sulcata-vs-hermann': '苏卡达 vs 赫曼 | 陆龟新手怎么选',
        'disease-treatment-detail': '龟病治疗指南 | 肺炎腐皮白眼症状与方案',
        'best-water-turtle': '水龟品种推荐 | 哪种水龟最好养',
        'chinese-turtles': '中国本土龟图鉴 | 草龟花龟黄喉',
        'turtle-secrets': '乌龟冷知识 | 10个养龟人才知道的秘密',
        'aquascape2': '龟缸造景攻略 | 打造低维护生态缸',
        'paludarium': '生态缸造景教程 | 仿野环境搭建',
        'turtle-anatomy': '乌龟身体密码 | 龟壳呼吸解剖',
        'care-details': '乌龟饲养详解 | 从开缸到喂食',
        'turtle-physiology2': '乌龟生理知识 | 体温与代谢',
        'turtle-physiology3': '乌龟生理知识 | 视觉听觉嗅觉',
        'water2': '水龟饲养指南 | 日常养护',
        'water3': '水龟常见问题 | 答疑解惑',
        'tortoise2': '陆龟饲养指南 | 环境搭建',
        'tortoise3': '陆龟常见问题 | 答疑解惑',
        'semiaquatic-list': '半水龟品种推荐 | 黄缘闭壳龟',
        'semiaquatic2': '半水龟饲养指南',
        'semiaquatic3': '半水龟常见问题',
        'care2': '饲养进阶技巧',
        'care3': '饲养问题解答',
        'disease2': '疾病防治常见问题',
        'disease3': '疾病防治进阶',
        'seasonal2': '季节养护指南',
        'seasonal3': '季节养护问答',
        'expert-recommend': '专家推荐 | 养龟必备清单',
        'expert2': '专家问答',
        'expert3': '专家经验分享',
    }
    
    # 尝试精确匹配
    for key, value in title_map.items():
        if key in name:
            return value
    
    # 处理带日期的文件名
    date_match = re.match(r'^(\d{8})-', name)
    if date_match:
        clean_name = re.sub(r'^(\d{8})-', '', name)
        # 清理特殊字符
        clean_name = clean_name.replace('_', ' ').replace('-', ' ')
        return f'{clean_name} | 爱龟谷乌龟知识库'
    
    # 默认标题
    return f'{name.replace("-", " ").replace("_", " ")} | 爱龟谷乌龟知识库'


def generate_description_from_filename(filename):
    """从文件名生成描述"""
    name = filename.replace('.html', '').replace('.en', '')
    
    # 描述映射表
    desc_map = {
        'musk-turtle': '麝香龟的饲养方法、水温要求、喂食技巧和常见问题解答，适合新手入门的蛋龟品种。',
        'hibernation': '乌龟冬眠前的准备、冬眠介质选择、温度控制和苏醒注意事项，实测数据告诉你最佳冬眠区间。',
        'newbie-guide': '新手养龟必看！草龟、巴西龟、花龟怎么选？开缸、喂食、换水全攻略。',
        'sulcata-vs-hermann': '苏卡达陆龟和赫曼陆龟对比：体型、温度、湿度、饮食要求，哪个更适合你？',
        'disease-treatment-detail': '乌龟肺炎、腐皮、白眼病的症状识别和居家治疗方案，结合50+病例样本总结。',
        'best-water-turtle': '水龟品种推荐：地图龟、火焰龟、麝香龟、剃刀龟，哪种最适合家养？',
        'chinese-turtles': '中国本土龟介绍：草龟、花龟、黄喉拟水龟的保育级别、外观特征和饲养要点。',
        'turtle-secrets': '乌龟没有声带？龟壳有神经？用屁股呼吸？颠覆认知的乌龟冷知识合集。',
        'aquascape2': '龟缸造景教程：从底砂选择到植物搭配，打造低维护的仿野生态缸。',
        'paludarium': '生态缸造景指南：水陆两栖环境搭建，适合半水龟和观赏鱼混养。',
        'turtle-anatomy': '乌龟解剖学：龟壳结构、呼吸方式、感官系统，一文读懂乌龟身体密码。',
    }
    
    for key, value in desc_map.items():
        if key in name:
            return value
    
    return f'爱龟谷乌龟知识库文章，提供专业的乌龟饲养科普内容，帮助龟友解决养龟问题。'


def batch_add_schema(article_dir=ARTICLE_DIR):
    """
    批量为article目录下所有HTML文件添加Schema
    """
    if not os.path.exists(article_dir):
        print(f"❌ 目录不存在: {article_dir}")
        return
    
    # 获取所有HTML文件
    html_files = [f for f in os.listdir(article_dir) if f.endswith('.html')]
    
    if not html_files:
        print("❌ 没有找到HTML文件")
        return
    
    print(f"\n📁 找到 {len(html_files)} 个HTML文件")
    print("-" * 50)
    
    success_count = 0
    skip_count = 0
    
    for filename in html_files:
        file_path = os.path.join(article_dir, filename)
        
        # 从文件名生成标题和描述
        title = generate_title_from_filename(filename)
        description = generate_description_from_filename(filename)
        
        if add_schema_to_html(file_path, title, description):
            success_count += 1
        else:
            skip_count += 1
    
    print("-" * 50)
    print(f"📊 完成: 成功 {success_count} 个，跳过 {skip_count} 个")
    
    return success_count


# ==================== Sitemap 相关函数 ====================

def generate_sitemap(article_dir=ARTICLE_DIR):
    """
    自动生成 sitemap.xml
    """
    print("\n📝 生成 sitemap.xml...")
    
    base_url = SITE_URL
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  
  <!-- 首页 -->
  <url>
    <loc>{base_url}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- 分类页面 -->
  <url>
    <loc>{base_url}/category/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <url>
    <loc>{base_url}/zh/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <!-- 文章页面 -->
'''
    
    # 添加所有文章
    if os.path.exists(article_dir):
        for filename in sorted(os.listdir(article_dir)):
            if filename.endswith('.html'):
                # 获取文件的最后修改时间
                file_path = os.path.join(article_dir, filename)
                lastmod = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                
                # 判断优先级
                priority = '0.8' if any(k in filename for k in ['guide', 'care', 'disease', 'hibernation', 'musk']) else '0.7'
                
                xml += f'''  <url>
    <loc>{base_url}/{article_dir}/{filename}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{priority}</priority>
  </url>
'''
    
    xml += '</urlset>'
    
    # 写入文件
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write(xml)
    
    print(f"✅ sitemap.xml 已生成，包含 {len([f for f in os.listdir(article_dir) if f.endswith('.html')])} 篇文章")
    return True


# ==================== Google 通知函数 ====================

def ping_google():
    """通知 Google 站点地图已更新"""
    try:
        sitemap_url = f"{SITE_URL}/{SITEMAP_FILE}"
        ping_url = f"https://www.google.com/ping?sitemap={sitemap_url}"
        
        response = requests.get(ping_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 已通知 Google 更新")
            return True
        else:
            print(f"⚠️ Google 通知返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google 通知失败: {e}")
        return False


# ==================== 主函数 ====================

def main():
    """主函数：执行所有SEO优化任务"""
    print("=" * 50)
    print("🐢 爱龟谷 SEO 自动优化脚本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. 添加 Schema 到所有文章
    print("\n【步骤 1/3】添加 Schema 结构化数据")
    schema_count = batch_add_schema()
    
    # 2. 生成 sitemap
    print("\n【步骤 2/3】生成站点地图")
    generate_sitemap()
    
    # 3. 通知 Google
    print("\n【步骤 3/3】通知搜索引擎")
    ping_google()
    
    print("\n" + "=" * 50)
    print("🎉 SEO 优化完成！")
    print("=" * 50)


# ==================== 单独运行 ====================

if __name__ == "__main__":
    # 如果直接运行此脚本，执行完整流程
    main()
