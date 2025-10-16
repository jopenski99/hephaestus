import asyncio
from crawl4ai import AsyncWebCrawler

class CrawlerHandler:
    def __init__(self):
        self.crawler = None

    async def init_crawler(self):
        """Initialize AsyncWebCrawler."""
        self.crawler = AsyncWebCrawler()
        await self.crawler.__aenter__()

    async def close_crawler(self):
        """Gracefully shutdown crawler."""
        if self.crawler:
            await self.crawler.__aexit__(None, None, None)

    async def crawl(self, url: str):
        """Crawl with optimal config for news sites."""
        result = await self.crawler.arun(
            url=url,
            js_render=True,
            wait_until="networkidle",
            extract_main_content=True,
            cache_mode="bypass",
            screenshot=False,  # keep off unless debugging
        )
        return result

async def test_crawler(): 
    handler = CrawlerHandler() 
    await handler.init_crawler() 
    try: 
        await handler.basic_crawl("https://example.com") 
        await handler.advanced_crawl("https://news.google.com/") 
    finally: await handler.close_crawler() 
    
if __name__ == "__main__": 
    asyncio.run(test_crawler())