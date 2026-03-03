"""
BASED MONEY - Cron Scheduler
Schedules automated tasks (weekly reallocation, monthly review, daily memos)
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import traceback
from typing import Callable, Optional


class CronScheduler:
    """
    Background scheduler for automated trading tasks.
    
    Uses APScheduler to run:
    - Weekly reallocation (Sundays 00:00 UTC)
    - Monthly theme review (1st of month 00:00 UTC)
    - Daily IC memo generation (daily at 23:00 UTC)
    """
    
    def __init__(self):
        """Initialize background scheduler."""
        self.scheduler = BackgroundScheduler(timezone='UTC')
        self.jobs = {}
        
    def schedule_weekly_reallocation(self, callback: Callable) -> None:
        """
        Schedule weekly capital reallocation.
        
        Args:
            callback: Function to call (should be orchestrator.weekly_reallocation_check)
        
        Runs every Sunday at 00:00 UTC.
        """
        try:
            trigger = CronTrigger(
                day_of_week='sun',
                hour=0,
                minute=0,
                timezone='UTC'
            )
            
            job = self.scheduler.add_job(
                func=self._safe_wrapper(callback, 'weekly_reallocation'),
                trigger=trigger,
                id='weekly_reallocation',
                name='Weekly Capital Reallocation',
                replace_existing=True
            )
            
            self.jobs['weekly_reallocation'] = job
            print("✓ Scheduled weekly reallocation (Sundays 00:00 UTC)")
            
        except Exception as e:
            print(f"⚠️ Failed to schedule weekly reallocation: {e}")
    
    def schedule_monthly_review(self, callback: Callable) -> None:
        """
        Schedule monthly theme rotation.
        
        Args:
            callback: Function to call (should be orchestrator.monthly_theme_review)
        
        Runs on 1st of each month at 00:00 UTC.
        """
        try:
            trigger = CronTrigger(
                day=1,
                hour=0,
                minute=0,
                timezone='UTC'
            )
            
            job = self.scheduler.add_job(
                func=self._safe_wrapper(callback, 'monthly_review'),
                trigger=trigger,
                id='monthly_review',
                name='Monthly Theme Review',
                replace_existing=True
            )
            
            self.jobs['monthly_review'] = job
            print("✓ Scheduled monthly review (1st of month 00:00 UTC)")
            
        except Exception as e:
            print(f"⚠️ Failed to schedule monthly review: {e}")
    
    def schedule_daily_ic_memo(self, callback: Callable) -> None:
        """
        Schedule daily IC memo generation.
        
        Args:
            callback: Function to call (should be orchestrator.generate_ic_memo)
        
        Runs daily at 23:00 UTC (end of trading day).
        """
        try:
            trigger = CronTrigger(
                hour=23,
                minute=0,
                timezone='UTC'
            )
            
            job = self.scheduler.add_job(
                func=self._safe_wrapper(callback, 'daily_ic_memo'),
                trigger=trigger,
                id='daily_ic_memo',
                name='Daily IC Memo',
                replace_existing=True
            )
            
            self.jobs['daily_ic_memo'] = job
            print("✓ Scheduled daily IC memo (23:00 UTC)")
            
        except Exception as e:
            print(f"⚠️ Failed to schedule daily IC memo: {e}")
    
    def start(self) -> None:
        """Start the scheduler."""
        try:
            self.scheduler.start()
            print("\n✅ Scheduler started")
            self._print_schedule()
        except Exception as e:
            print(f"❌ Failed to start scheduler: {e}")
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler.
        
        Args:
            wait: If True, wait for running jobs to complete
        """
        try:
            self.scheduler.shutdown(wait=wait)
            print("✅ Scheduler stopped")
        except Exception as e:
            print(f"⚠️ Failed to stop scheduler: {e}")
    
    def run_now(self, job_id: str) -> None:
        """
        Manually trigger a scheduled job immediately.
        
        Args:
            job_id: Job identifier ('weekly_reallocation', 'monthly_review', 'daily_ic_memo')
        """
        if job_id in self.jobs:
            try:
                job = self.jobs[job_id]
                job.func()
                print(f"✓ Manually triggered: {job_id}")
            except Exception as e:
                print(f"❌ Failed to run {job_id}: {e}")
        else:
            print(f"⚠️ Unknown job: {job_id}")
    
    def _safe_wrapper(self, callback: Callable, job_name: str) -> Callable:
        """
        Wrap callback with error handling and logging.
        
        Args:
            callback: Function to wrap
            job_name: Name for logging
        
        Returns:
            Wrapped function
        """
        def wrapper():
            print(f"\n{'='*60}")
            print(f"🔔 SCHEDULED JOB: {job_name}")
            print(f"   Time: {datetime.now().isoformat()}")
            print(f"{'='*60}\n")
            
            try:
                callback()
                print(f"\n✅ {job_name} completed successfully\n")
                
            except Exception as e:
                error_msg = f"❌ {job_name} failed: {e}"
                print(f"\n{error_msg}")
                print(f"Traceback:\n{traceback.format_exc()}\n")
                
                # Log error to database
                try:
                    from database.db import record_event
                    record_event(
                        event_type=f"scheduled_job_error",
                        details={
                            "job_name": job_name,
                            "error": str(e),
                            "traceback": traceback.format_exc()
                        },
                        severity="error"
                    )
                except Exception as log_error:
                    print(f"⚠️ Failed to log error: {log_error}")
        
        return wrapper
    
    def _print_schedule(self) -> None:
        """Print current job schedule."""
        print("\n📅 Scheduled Jobs:")
        for job_id, job in self.jobs.items():
            next_run = job.next_run_time
            print(f"  - {job.name}: {next_run.strftime('%Y-%m-%d %H:%M UTC') if next_run else 'Not scheduled'}")
        print()
    
    def get_next_run_times(self) -> dict:
        """
        Get next run times for all scheduled jobs.
        
        Returns:
            Dictionary mapping job_id to next_run_time
        """
        return {
            job_id: job.next_run_time.isoformat() if job.next_run_time else None
            for job_id, job in self.jobs.items()
        }
    
    def is_running(self) -> bool:
        """
        Check if scheduler is running.
        
        Returns:
            True if scheduler is active
        """
        return self.scheduler.running
