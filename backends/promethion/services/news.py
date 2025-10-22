       
from typing import Any
from sqlmodel import Session, select
from datetime import datetime
from promethion.services.news_crawler import NewsCrawler
from promethion.services.llm_handler import LLMHandler
from promethion.services.rag_query import RAGQueryEngine
from promethion.api.core.config import settings



news_source = [
    {"name": "Mindanao Times", "url": "https://www.mindanaotimes.com.ph/category/news/"},
]

class News:
    def __init__(self, model: dict = None):
        self.model = model
    
    async def acquire_news(user: Any = None):
        
        
        nc = NewsCrawler()
        results = []
        for source in news_source:
            articles = await nc.crawl_outlet(source["name"], source["url"])
            results.append(articles)
        return results
    
    async def process_news(self, text:str, type: str, context_data: str = None,variant: str = "default"):
        today = datetime.today().strftime("%Y-%m-%d")
        context = context_data
        llm = LLMHandler(model=self.model['model'], base_url=self.model["base_url"], api_key=self.model["api_key"], port=self.model["port"])
        if context is None:
            rag = RAGQueryEngine()
            context = rag.query_by_date(date=today,query=text)
        response = llm.handleLLM(text,type,context,variant)
        
        return response
        
    async def direct_query(self, text:str, type: str, context: str = None,variant: str = "default"):
        llm = LLMHandler(model=self.model['model'], base_url=self.model["base_url"], api_key=self.model["api_key"], port=self.model["port"])
        response = llm.handleLLM(text,type,context,variant)
        
        return response
    

