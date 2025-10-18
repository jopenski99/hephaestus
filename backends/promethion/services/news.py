       
from typing import Any
from sqlmodel import Session, select
from datetime import datetime
from promethion.models.news_source import NewsSource
from promethion.services.news_crawler import NewsCrawler




news_source = [
    {"name": "Mindanao Times", "url": "https://www.mindanaotimes.com.ph/category/news/"},
]

class News:
    def get_all_sources(db: Session):
        return db.exec(select(NewsSource)).all()
    
    async def acquire_news(user: Any = None):
        
        
        nc = NewsCrawler()
        results = []
        for source in news_source:
            articles = await nc.crawl_outlet(source["name"], source["url"])
            results.append(articles)
        return results

