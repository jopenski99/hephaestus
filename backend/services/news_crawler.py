from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

async def crawl_news(name:str,url:str):
    if name.lower() == "mindanaotimes":
        return await crawl_mindanao_news()
    
  
async def crawl_mindanao_news():
    config = CrawlerRunConfig(
        cache_mode="bypass",
        wait_until="networkidle",
        max_depth=1,
        headless=True
    )

    async with AsyncWebCrawler(config) as crawler:
        result = await crawler.run("https://www.mindanaotimes.com.ph/category/news/")
        html = result.page_content

        # Parse with BeautifulSoup to filter only relevant data
        soup = BeautifulSoup(html, "html.parser")

        articles = []
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        for header in soup.select("div.header-list-style"):
            title_tag = header.select_one("h2.penci-entry-title a")
            date_tag = header.select_one("time.entry-date.published")

            if not title_tag or not date_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href")

            # Parse the datetime attribute from <time datetime="...">
            raw_date = date_tag.get("datetime")
            try:
                article_date = datetime.fromisoformat(raw_date).date()
            except Exception:
                continue

            # Filter only today or yesterday
            if article_date in [today, yesterday]:
                articles.append({
                    "title": title,
                    "url": link,
                    "date": article_date.isoformat()
                })

        print(articles)

        # Optional: follow each article link for full content
        for art in articles:
            article_page = await crawler.run(art["url"])
            content = BeautifulSoup(article_page.page_content, "html.parser").select_one("div.td-post-content")
            art["content"] = content.get_text(strip=True) if content else None

        return articles
