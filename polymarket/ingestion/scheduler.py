"""
BASED MONEY - Ingestion Scheduler
Schedules periodic data fetching from external sources
"""

import sys
import time
from datetime import datetime

sys.path.insert(0, "..")

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ingestion.polymarket import fetch_markets
from ingestion.news import fetch_news
from ingestion.filters import filter_tradeable_markets
from database import save_market, record_event

# Global scheduler instance
scheduler = None


def fetch_and_save_markets():
    """
    Job: Fetch markets from Polymarket, filter, and save to database.
    Runs every 5 minutes.
    """
    try:
        print("\n" + "=" * 60)
        print(
            f"🔄 MARKET FETCH JOB - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        print("=" * 60)

        # Step 1: Fetch markets
        markets = fetch_markets(limit=100, active_only=True)

        if not markets:
            print("⚠️ No markets fetched, skipping save")
            return

        # Step 2: Filter to tradeable markets
        tradeable = filter_tradeable_markets(markets)

        if not tradeable:
            print("⚠️ No tradeable markets after filtering")
            return

        # Step 3: Save to database
        saved_count = 0
        failed_count = 0

        for market in tradeable:
            if save_market(market):
                saved_count += 1
            else:
                failed_count += 1

        print(f"\n✅ Saved {saved_count} markets to database")
        if failed_count > 0:
            print(f"⚠️ Failed to save {failed_count} markets")

        # Log job completion
        record_event(
            event_type="scheduler_job_completed",
            details={
                "job": "fetch_markets",
                "markets_fetched": len(markets),
                "markets_filtered": len(tradeable),
                "markets_saved": saved_count,
                "markets_failed": failed_count,
            },
            severity="info",
        )

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error in market fetch job: {e}")
        record_event(
            event_type="scheduler_job_error",
            details={
                "job": "fetch_markets",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            severity="error",
        )


def fetch_and_save_news():
    """
    Job: Fetch news from RSS feeds and save to database.
    Runs every 15 minutes.
    """
    try:
        print("\n" + "=" * 60)
        print(
            f"📰 NEWS FETCH JOB - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        print("=" * 60)

        # Fetch news (returns NewsEvent objects, already saved to DB)
        # fetch_news() internally calls save_news_event() for each event
        events = fetch_news(hours_back=1)  # Only fetch last hour to avoid duplicates

        if not events:
            print("⚠️ No news events fetched")
        else:
            print(f"✅ Fetched and saved {len(events)} news events")

        # Log job completion
        record_event(
            event_type="scheduler_job_completed",
            details={"job": "fetch_news", "events_fetched": len(events)},
            severity="info",
        )

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error in news fetch job: {e}")
        record_event(
            event_type="scheduler_job_error",
            details={
                "job": "fetch_news",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            severity="error",
        )


def start_scheduler():
    """
    Start the ingestion scheduler with configured jobs.

    Jobs:
    - fetch_markets: Every 5 minutes
    - fetch_news: Every 15 minutes
    """
    global scheduler

    print("\n" + "=" * 60)
    print("BASED MONEY - Ingestion Scheduler Starting")
    print("=" * 60)

    # Create scheduler
    scheduler = BackgroundScheduler()

    # Job 1: Fetch markets every 5 minutes
    scheduler.add_job(
        func=fetch_and_save_markets,
        trigger=IntervalTrigger(minutes=5),
        id="fetch_markets",
        name="Fetch and save Polymarket markets",
        replace_existing=True,
    )
    print("✅ Scheduled: fetch_markets (every 5 minutes)")

    # Job 2: Fetch news every 15 minutes
    scheduler.add_job(
        func=fetch_and_save_news,
        trigger=IntervalTrigger(minutes=15),
        id="fetch_news",
        name="Fetch and save news events",
        replace_existing=True,
    )
    print("✅ Scheduled: fetch_news (every 15 minutes)")

    # Start scheduler
    scheduler.start()
    print("\n🚀 Scheduler started!")
    print("=" * 60)

    # Run jobs immediately on startup
    print("\n🔄 Running initial jobs...")
    fetch_and_save_markets()
    fetch_and_save_news()

    return scheduler


def stop_scheduler():
    """Stop the scheduler and wait for jobs to complete."""
    global scheduler

    if scheduler:
        print("\n⏹️  Stopping scheduler...")
        scheduler.shutdown(wait=True)
        print("✅ Scheduler stopped")
    else:
        print("⚠️ Scheduler not running")


def get_scheduler_status():
    """Get current scheduler status and job info."""
    global scheduler

    if not scheduler or not scheduler.running:
        return {"running": False, "jobs": []}

    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
        )

    return {"running": True, "jobs": jobs_info}


def run_test(duration_minutes=15):
    """
    Test the scheduler by running it for a specified duration.

    Args:
        duration_minutes: How long to run (default 15 minutes)
    """
    print("\n" + "=" * 60)
    print(f"SCHEDULER TEST - Running for {duration_minutes} minutes")
    print("=" * 60)

    # Start scheduler
    start_scheduler()

    # Run for specified duration
    print(f"\n⏱️  Running for {duration_minutes} minutes...")
    print("   (Press Ctrl+C to stop early)\n")

    start_time = time.time()
    duration_seconds = duration_minutes * 60

    try:
        while True:
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed

            if remaining <= 0:
                break

            # Print status every minute
            if int(elapsed) % 60 == 0 and int(elapsed) > 0:
                status = get_scheduler_status()
                print(f"\n📊 Status update ({int(elapsed/60)} min elapsed):")
                for job in status["jobs"]:
                    print(f"   {job['name']}: next run at {job['next_run']}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")

    # Stop scheduler
    stop_scheduler()

    print("\n" + "=" * 60)
    print("✅ Test complete")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Check Supabase tables:")
    print("      - markets table should have entries")
    print("      - news_events table should have entries")
    print("      - event_log should show job executions")
    print("   2. If both tables populated, scheduler is working!")
    print("   3. Commit code and proceed to next task")
    print()


if __name__ == "__main__":
    import sys

    # Parse command line args
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
            run_test(duration_minutes=duration)
        except ValueError:
            print("Usage: python scheduler.py [duration_in_minutes]")
            print("Example: python scheduler.py 15")
            sys.exit(1)
    else:
        # Default: run for 15 minutes
        run_test(duration_minutes=15)
