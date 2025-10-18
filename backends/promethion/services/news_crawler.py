from crawl4ai import *
import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
from typing import Any, List, Dict
from promethion.services.crawler import CrawlerHandler
from promethion.services.rag_ingestor import RAGIngestor

class NewsCrawler:
    def __init__(self):
        self.handler = CrawlerHandler()
        self.ingestor = RAGIngestor()
        self.concurrency = 5
    
    async def crawl_outlet(self, outlet_name: str, base_url: str) -> None:
        """Full flow: collect links -> fetch details -> push to RAG."""
        print(f"📰 Crawling {outlet_name} from {base_url}")
        await self.handler.init_crawler()

        try:
            # 1️⃣ Fetch page & extract article links
            doc = await self.handler.crawl(base_url)
            article_links = self.extract_links(doc.html)

            print(f"✅ Found {len(article_links)} candidate articles")

            # 2️⃣ Crawl articles concurrently with rate limit
            sem = asyncio.Semaphore(self.concurrency)
            tasks = [
                self.fetch_and_process_article(outlet_name, link, sem)
                for link in article_links
            ]
            await asyncio.gather(*tasks)
        finally:
            await self.handler.close_crawler()

    
    def extract_links(self, html: str) -> List[str]:
        """Extract only valid article URLs from Mindanao Times page."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        for header in soup.select("div.header-list-style"):
            title_tag = header.find("h2", class_="penci-entry-title")
            date_tag = header.find("time", class_="entry-date published")
            if not (title_tag and date_tag):
                continue

            link = title_tag.find("a").get("href")
            raw_date = date_tag.get("datetime")
            try:
                pub_date = datetime.fromisoformat(raw_date).date()
            except Exception:
                continue

            if pub_date in [today, yesterday]:
                links.append(link)
        return links
    async def fetch_and_process_article(self, outlet_name: str, link: str, sem: asyncio.Semaphore):
        """Fetch article content, parse and store to RAG."""
        async with sem:
            try:
                print(f"🔗 Fetching: {link}")
                doc = await self.handler.crawl(link)
                article_data = self.parse_article_detail(outlet_name, link, doc.html)
                
                # Optional: push to your RAG or DB
                await self.ingestor.ingest_article(article_data, category="News")
                print(f"✅ Processed: {article_data['title']}")

            except Exception as e:
                print(f"❌ Error processing {link}: {e}")

    def parse_article_detail(self, outlet_name: str, url: str, html: str) -> Dict[str, Any]:
        """Parse the main content of a single article."""
        soup = BeautifulSoup(html, "html.parser")
        content_tag = soup.find("div", class_="inner-post-entry entry-content")
        title_tag = soup.find("h1", class_="post-title single-post-title entry-title")

        return {
            "title": title_tag.get_text(strip=True) if title_tag else "Untitled",
            "content": content_tag.get_text(strip=True) if content_tag else "",
            "url": url,
            "source": outlet_name,
            "date": datetime.now().isoformat()
        }

async def main():
    """Manual test entrypoint."""
    crawler = NewsCrawler()
    news = await crawler.crawl_outlet("Mindanao Times", "https://www.mindanaotimes.com.ph/category/news/")
    print("Crawling completed.")
    print(news)
    return news



if __name__ == "__main__":
    asyncio.run(main())