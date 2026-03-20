import hashlib
import json
import os
from datetime import datetime

class ContentDeduplicator:
    def __init__(self, db_path="../data/articles_db.json"):
        self.db_path = db_path
        self.load_db()
    
    def load_db(self):
        """加载数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        except FileNotFoundError:
            self.db = {"articles": [], "hashes": []}
    
    def save_db(self):
        """保存数据库"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)
    
    def generate_hash(self, title, content):
        """生成内容唯一标识"""
        text = f"{title}{content[:200]}".encode('utf-8')
        return hashlib.sha256(text).hexdigest()[:16]
    
    def is_duplicate(self, title, content):
        """检查是否重复"""
        content_hash = self.generate_hash(title, content)
        return content_hash in self.db["hashes"]
    
    def add_article(self, article):
        """添加新文章到数据库"""
        content_hash = self.generate_hash(
            article["title"], 
            article.get("content", "")
        )
        article["id"] = content_hash
        article["added_date"] = datetime.now().isoformat()
        
        self.db["articles"].append(article)
        self.db["hashes"].append(content_hash)
        self.save_db()
