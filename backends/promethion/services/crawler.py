import sys
import asyncio
import threading
from crawl4ai import AsyncWebCrawler
        

class CrawlerHandler:
    def __init__(self):
        self.is_windows = sys.platform.startswith("win")
        self.crawler = None
        self.loop = None
        self.thread = None


    async def init_crawler(self):

        if not self.is_windows:
            # Native async init for Linux/WSL/mac
            self.crawler = AsyncWebCrawler()
            await self.crawler.__aenter__()
            print("✅ Crawler initialized (async mode).")
            return
        # Initialize only once
        self.crawler = AsyncWebCrawler()
        print("⚙️ Initializing Windows-safe crawler in background thread...")

        # Start a dedicated event loop thread once
        if not self.thread:
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()

        # Run init on that dedicated loop
        fut = asyncio.run_coroutine_threadsafe(self._init_in_loop(), self.loop)
        await asyncio.wrap_future(fut)
        print("✅ Crawler initialized (Windows thread-safe mode).")
        
    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _init_in_loop(self):
        self.crawler = AsyncWebCrawler()
        await self.crawler.__aenter__()

        
    def _init_crawler_blocking(self):
        """Fallback for Windows when asyncio subprocess is unsupported."""
        # On Windows, this call will block but avoid NotImplementedError
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        crawler = AsyncWebCrawler()
        loop.run_until_complete(crawler.__aenter__())
        self.crawler = crawler
        
    async def close_crawler(self):
        """Gracefully close async crawler if used."""
        if not self.crawler:
            return
        if self.is_windows:
            fut = asyncio.run_coroutine_threadsafe(
                self.crawler.__aexit__(None, None, None), self.loop
            )
            await asyncio.wrap_future(fut)
        else:
            await self.crawler.__aexit__(None, None, None)
        print("✅ Crawler closed.")

    async def crawl(self, url: str):
        """Perform crawl safely across OS."""
        if not self.crawler:
            raise RuntimeError("Crawler not initialized")

        if self.is_windows:
            fut = asyncio.run_coroutine_threadsafe(
                self._crawl_in_loop(url), self.loop
            )
            return await asyncio.wrap_future(fut)
        else:
            return await self.crawler.arun(
                url=url,
                cache_mode="bypass",
                wait_until="networkidle",
                js_render=True,
                extract_main_content=True,
            )
    async def _crawl_in_loop(self, url: str):
        return await self.crawler.arun(
            url=url,
            cache_mode="bypass",
            wait_until="networkidle",
            js_render=True,
            extract_main_content=True,
        )   
    def _crawl_blocking(self, url: str):
        """Fallback synchronous crawl."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        crawler = AsyncWebCrawler()
        result = loop.run_until_complete(crawler.arun(
            url=url,
            cache_mode="bypass",
            wait_until="networkidle",
            js_render=True,
            extract_main_content=True
        ))
        loop.run_until_complete(crawler.__aexit__(None, None, None))
        return result
        
    def _crawl_sync(self, url: str):
        """Synchronous crawl wrapper for Windows."""
        with self.crawler as crawler:
            result = crawler.run(
                url=url,
                cache_mode="bypass",
                wait_until="networkidle",
                js_render=True,
                extract_main_content=True
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