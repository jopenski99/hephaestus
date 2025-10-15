from typing import Any
from sqlmodel import Session, select
from datetime import datetime
from backend.models.news_source import NewsSource

class News:
    def get_all_sources(db: Session):
        return db.exec(select(NewsSource)).all()
    
    def add_source(db: Session, name: str, url: str):
        source = NewsSource(outlet_name=name, domain=url)
        db.add(source)
        db.commit()
        db.refresh(source)
        return source
    
    def update_crawl_time(db: Session, source_id: int):
        source = db.get(NewsSource, source_id)
        if source:
            source.last_crawled = datetime.utcnow()
            db.add(source)
            db.commit()
            db.refresh(source)
        return source
