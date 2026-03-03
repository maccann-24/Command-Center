"""
BASED MONEY - Scheduler Tests
Test cron scheduling for automated tasks
"""

import sys
import os
import time

# Set up test environment
os.environ['TRADING_MODE'] = 'paper'
os.environ['SUPABASE_URL'] = 'http://localhost:54321'
os.environ['SUPABASE_KEY'] = 'test_key'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scheduler import CronScheduler


# Global flag for callback testing
callback_called = False


def test_callback():
    """Test callback function."""
    global callback_called
    callback_called = True
    print("Test callback executed!")


def test_scheduler_initialization():
    """Test that scheduler initializes correctly."""
    print("\n" + "="*60)
    print("TEST: Scheduler Initialization")
    print("="*60)
    
    scheduler = CronScheduler()
    
    assert scheduler.scheduler is not None
    assert scheduler.jobs == {}
    assert not scheduler.is_running()
    
    print("✅ PASSED: Scheduler initialized")


def test_schedule_weekly_reallocation():
    """Test scheduling weekly reallocation job."""
    print("\n" + "="*60)
    print("TEST: Schedule Weekly Reallocation")
    print("="*60)
    
    scheduler = CronScheduler()
    
    # Schedule the job
    scheduler.schedule_weekly_reallocation(test_callback)
    
    # Verify job was added
    assert 'weekly_reallocation' in scheduler.jobs
    assert scheduler.jobs['weekly_reallocation'].id == 'weekly_reallocation'
    
    print("✅ PASSED: Weekly reallocation scheduled")
    print(f"   Job ID: weekly_reallocation")
    

def test_schedule_monthly_review():
    """Test scheduling monthly theme review job."""
    print("\n" + "="*60)
    print("TEST: Schedule Monthly Review")
    print("="*60)
    
    scheduler = CronScheduler()
    
    # Schedule the job
    scheduler.schedule_monthly_review(test_callback)
    
    # Verify job was added
    assert 'monthly_review' in scheduler.jobs
    assert scheduler.jobs['monthly_review'].id == 'monthly_review'
    
    print("✅ PASSED: Monthly review scheduled")
    print(f"   Job ID: monthly_review")


def test_schedule_daily_ic_memo():
    """Test scheduling daily IC memo generation."""
    print("\n" + "="*60)
    print("TEST: Schedule Daily IC Memo")
    print("="*60)
    
    scheduler = CronScheduler()
    
    # Schedule the job
    scheduler.schedule_daily_ic_memo(test_callback)
    
    # Verify job was added
    assert 'daily_ic_memo' in scheduler.jobs
    assert scheduler.jobs['daily_ic_memo'].id == 'daily_ic_memo'
    
    print("✅ PASSED: Daily IC memo scheduled")
    print(f"   Job ID: daily_ic_memo")


def test_scheduler_start_stop():
    """Test starting and stopping the scheduler."""
    print("\n" + "="*60)
    print("TEST: Scheduler Start/Stop")
    print("="*60)
    
    scheduler = CronScheduler()
    
    # Start scheduler
    scheduler.start()
    assert scheduler.is_running()
    print("✓ Scheduler started")
    
    # Stop scheduler
    scheduler.shutdown(wait=False)
    time.sleep(0.1)  # Give it a moment to shutdown
    assert not scheduler.is_running()
    print("✓ Scheduler stopped")
    
    print("✅ PASSED: Start/stop works correctly")


def test_run_now():
    """Test manually triggering a job."""
    print("\n" + "="*60)
    print("TEST: Manual Job Trigger (run_now)")
    print("="*60)
    
    global callback_called
    callback_called = False
    
    scheduler = CronScheduler()
    scheduler.schedule_weekly_reallocation(test_callback)
    scheduler.start()
    
    # Manually trigger the job
    scheduler.run_now('weekly_reallocation')
    
    # Verify callback was called
    assert callback_called, "Callback should have been called"
    
    scheduler.shutdown(wait=False)
    
    print("✅ PASSED: Manual job trigger works")


def test_get_next_run_times():
    """Test getting next run times for scheduled jobs."""
    print("\n" + "="*60)
    print("TEST: Get Next Run Times")
    print("="*60)
    
    scheduler = CronScheduler()
    scheduler.schedule_weekly_reallocation(test_callback)
    scheduler.schedule_monthly_review(test_callback)
    scheduler.start()
    
    next_run_times = scheduler.get_next_run_times()
    
    assert 'weekly_reallocation' in next_run_times
    assert 'monthly_review' in next_run_times
    assert next_run_times['weekly_reallocation'] is not None
    assert next_run_times['monthly_review'] is not None
    
    scheduler.shutdown(wait=False)
    
    print("✅ PASSED: Get next run times works")
    print(f"   Weekly reallocation: {next_run_times['weekly_reallocation']}")
    print(f"   Monthly review: {next_run_times['monthly_review']}")


def test_all_jobs_scheduled():
    """Test that all three jobs can be scheduled together."""
    print("\n" + "="*60)
    print("TEST: All Jobs Scheduled Together")
    print("="*60)
    
    scheduler = CronScheduler()
    
    # Schedule all jobs
    scheduler.schedule_weekly_reallocation(test_callback)
    scheduler.schedule_monthly_review(test_callback)
    scheduler.schedule_daily_ic_memo(test_callback)
    
    # Verify all jobs present
    assert len(scheduler.jobs) == 3
    assert 'weekly_reallocation' in scheduler.jobs
    assert 'monthly_review' in scheduler.jobs
    assert 'daily_ic_memo' in scheduler.jobs
    
    scheduler.start()
    
    # Get schedule
    next_runs = scheduler.get_next_run_times()
    assert len(next_runs) == 3
    
    scheduler.shutdown(wait=False)
    
    print("✅ PASSED: All 3 jobs scheduled correctly")
    for job_id, next_run in next_runs.items():
        print(f"   - {job_id}: {next_run}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCHEDULER TESTS")
    print("="*60)
    
    # Run all tests
    test_scheduler_initialization()
    test_schedule_weekly_reallocation()
    test_schedule_monthly_review()
    test_schedule_daily_ic_memo()
    test_scheduler_start_stop()
    test_run_now()
    test_get_next_run_times()
    test_all_jobs_scheduled()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)
