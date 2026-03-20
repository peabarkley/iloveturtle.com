def apply_article_template(metadata, lang="zh"):
    """将采集的内容转换为爱龟谷文章格式"""
    
    if lang == "zh":
        site_name = "爱龟谷"
        site_subtitle = "turtle · 知识库 | 综合科普"
        lang_switch = '<a href="/zh/">English</a>'
    else:
        site_name = "Aiguigu"
        site_subtitle = "turtle · knowledge base"
        lang_switch = '<a href="/">中文</a>'
    
    # 简单的分类名称映射
    category_names = {
        "facts-disruption": "颠覆认知",
        "facts-physiology": "神奇生理",
        "facts-beginner": "新手避坑",
        "species-tortoise": "陆龟",
        "species-water": "水龟",
        "species-semiaquatic": "半水栖龟",
        "care-essentials": "饲养要点",
        "care-aquascape": "造景生态",
        "care-seasonal": "季节提醒",
        "disease-treatment": "疾病防治",
        "disease-expert": "专家推荐"
    }
    
    category_name = category_names.get(metadata['category'], metadata['category'])
    
    template = f"""<!DOCTYPE html>
<html lang="{'zh-CN' if lang=='zh' else 'en'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']} - {site_name}</title>
    <meta name="description" content="{metadata.get('excerpt', metadata['content'][:150])}">
    <meta name="keywords" content="乌龟,{category_name},养龟,{metadata['source']}">
    <link rel="stylesheet" href="/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <header class="header">
        <div class="container header-content">
            <div class="logo-area">
                <div class="logo-icon"><i class="fas fa-turtle"></i></div>
                <div class="logo-text">
                    <h1>{site_name}</h1>
                    <p>{site_subtitle}</p>
                </div>
            </div>
            <div class="nav-wrapper">
                <nav class="nav-links">
                    <a href="/index.html">{'首页' if lang=='zh' else 'Home'}</a>
                    <a href="/category/facts.html">{'冷知识' if lang=='zh' else 'Fun Facts'}</a>
                    <a href="/category/species.html">{'品种' if lang=='zh' else 'Species'}</a>
                    <a href="/category/care.html">{'饲养' if lang=='zh' else 'Care'}</a>
                    <a href="/category/disease.html">{'疾病' if lang=='zh' else 'Health'}</a>
                </nav>
                <div class="lang-switch">{lang_switch}</div>
            </div>
        </div>
    </header>

    <div class="breadcrumb container">
        <a href="/index.html">{'首页' if lang=='zh' else 'Home'}</a> &gt; 
        <a href="/category/{metadata['category'].split('-')[0]}.html">{category_name}</a> &gt; 
        <span>{metadata['title']}</span>
    </div>

    <div class="article-container">
        <div class="article-header">
            <h1>{metadata['title']}</h1>
            <div class="article-meta">
                <span><i class="far fa-calendar-alt"></i> {metadata['date']}</span>
                <span><i class="far fa-eye"></i> {'正在加载' if lang=='zh' else 'loading'}</span>
                <span><i class="far fa-user"></i> {site_name}</span>
                <span><i class="fas fa-link"></i> {'来源' if lang=='zh' else 'Source'}: <a href="{metadata['url']}" target="_blank">{metadata['source']}</a></span>
            </div>
        </div>
        
        <div class="article-content">
            {metadata['content']}
        </div>

        <div class="article-footer">
            <span>{'分类' if lang=='zh' else 'Category'}: <a href="/category/{metadata['category'].split('-')[0]}.html">{category_name}</a></span>
            <span>{'标签' if lang=='zh' else 'Tags'}: <a href="#">#{'采集' if lang=='zh' else 'auto'}</a> <a href="#">#{metadata['source']}</a></span>
        </div>

        <div class="notice-board" style="background: #fff3cd; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p><i class="fas fa-info-circle"></i> 
            {'本文由爱龟谷自动采集系统生成，内容来源于网络公开信息。如需删除或修改，请联系我们。' if lang=='zh' else 
            'This article is automatically generated. Content from public online sources. Contact us for removal.'}
            </p>
        </div>
    </div>

    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-col"><h5>{site_name}</h5><ul><li><a href="#">{'关于我们' if lang=='zh' else 'About Us'}</a></li><li><a href="#">{'内容准则' if lang=='zh' else 'Guidelines'}</a></li><li><a href="#">{'商务合作' if lang=='zh' else 'Cooperation'}</a></li></ul></div>
                <div class="footer-col"><h5>{'探索' if lang=='zh' else 'Explore'}</h5><ul><li><a href="/category/facts.html">{'冷知识库' if lang=='zh' else 'Fun Facts'}</a></li><li><a href="/category/species.html">{'品种大全' if lang=='zh' else 'Species'}</a></li><li><a href="/category/disease.html">{'疾病自诊' if lang=='zh' else 'Health'}</a></li></ul></div>
                <div class="footer-col"><h5>{'互动' if lang=='zh' else 'Interact'}</h5><ul><li><a href="#"><i class="fab fa-weixin"></i> {'公众号' if lang=='zh' else 'WeChat'}</a></li><li><a href="#">{'龟友圈' if lang=='zh' else 'Community'}</a></li><li>{lang_switch}</li></ul></div>
            </div>
            <div class="copyright">© 2026 {site_name} · {'乌龟综合科普库' if lang=='zh' else 'Turtle Knowledge Base'}</div>
        </div>
    </footer>

    <script src="/script.js"></script>
</body>
</html>
"""
    return template
