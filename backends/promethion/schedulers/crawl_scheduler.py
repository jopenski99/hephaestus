# backend/scheduler/crawl_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from contextlib import contextmanager
import traceback

from backend.database import get_session
from backend.services.news import get_all_sources, update_crawl_time
from backend.services.news_crawler import crawl_domain

@contextmanager
def get_db():
    """Context-managed DB session."""
    db = next(get_session())
    try:
        yield db
    finally:
        db.close()

def scheduled_crawl():
    """Main crawling task that runs on schedule."""
    print("🕑 Running scheduled crawl job...")
    with get_db() as db:
        sources = get_all_sources(db)
        for src in sources:
            print(f"📰 Crawling {src.outlet_name} ({src.domain})...")
            try:
                crawl_domain(src.domain)
                update_crawl_time(db, src.id)
                db.commit()
                print(f"✅ {src.outlet_name} crawl complete.")
            except Exception as e:
                db.rollback()
                print(f"❌ Error crawling {src.domain}: {e}")
                traceback.print_exc()

def start_scheduler():
    """Initializes and starts the background scheduler."""
    scheduler = BackgroundScheduler(timezone="Asia/Manila")

    # Schedule at 2:30 AM daily
    scheduler.add_job(
        scheduled_crawl,
        CronTrigger(hour=2, minute=30),
        id="daily_news_crawl",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler started — daily crawl set for 2:30 AM (Asia/Manila).")
    return scheduler
