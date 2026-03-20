class ArticleClassifier:
    def __init__(self):
        self.category_keywords = {
            "facts-disruption": ["冷知识", "颠覆", "居然", "真相", "秘密", "不知道"],
            "facts-physiology": ["生理", "解剖", "呼吸", "眼睛", "壳", "骨骼"],
            "facts-beginner": ["新手", "入门", "选择", "推荐", "第一次", "避坑"],
            "species-tortoise": ["陆龟", "苏卡达", "赫曼", "红腿", "豹龟"],
            "species-water": ["水龟", "巴西龟", "草龟", "麝香", "剃刀", "蛋龟"],
            "species-semiaquatic": ["半水", "黄缘", "枫叶", "锯缘", "闭壳龟"],
            "care-essentials": ["饲养", "水质", "温度", "喂食", "光照", "UVB"],
            "care-aquascape": ["造景", "生态缸", "植物", "底砂", "沉木", "过滤"],
            "care-seasonal": ["冬眠", "季节", "夏天", "冬天", "春秋", "换季"],
            "disease-treatment": ["疾病", "肺炎", "腐皮", "白眼", "治疗", "症状"],
            "disease-expert": ["专家", "兽医", "经验", "建议", "访谈", "误区"]
        }
    
    def classify(self, title, content):
        """根据关键词自动分类"""
        text = f"{title} {content}".lower()
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for kw in keywords:
                if kw.lower() in text:
                    score += 1
            if score > 0:
                scores[category] = score
        
        if not scores:
            return "care-essentials"  # 默认分类
        
        return max(scores, key=scores.get)
