"""
Background Job Scheduler for SmartTrip
======================================

Uses APScheduler BackgroundScheduler to run jobs in-process with Flask.
This avoids the need for separate cron services (Render Free Tier compatible).

Jobs:
- Aggregate Trip Interactions: Hourly at :00
- Cleanup Sessions: Every 15 minutes
- Aggregate Daily Metrics: Daily at 02:00 UTC
"""

import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging for scheduler
logging.basicConfig(level=logging.INFO)
scheduler_logger = logging.getLogger('apscheduler')
scheduler_logger.setLevel(logging.INFO)

# Create a separate logger for job execution
job_logger = logging.getLogger('scheduler.jobs')
job_logger.setLevel(logging.INFO)

# Global scheduler instance
_scheduler = None


def job_aggregate_interactions():
    """
    Wrapper for aggregate_trip_interactions job.
    Handles imports and logging.
    """
    job_logger.info("[SCHEDULER] Starting: Aggregate Trip Interactions")
    try:
        from scripts.aggregate_trip_interactions import aggregate_trip_interactions
        result = aggregate_trip_interactions()
        if result:
            job_logger.info("[SCHEDULER] Completed: Aggregate Trip Interactions - SUCCESS")
        else:
            job_logger.warning("[SCHEDULER] Completed: Aggregate Trip Interactions - FAILED")
    except Exception as e:
        job_logger.error(f"[SCHEDULER] Error in Aggregate Trip Interactions: {e}")


def job_cleanup_sessions():
    """
    Wrapper for cleanup_sessions job.
    Handles imports and logging.
    """
    job_logger.info("[SCHEDULER] Starting: Cleanup Sessions")
    try:
        from scripts.cleanup_sessions import cleanup_sessions
        result = cleanup_sessions()
        if result:
            job_logger.info("[SCHEDULER] Completed: Cleanup Sessions - SUCCESS")
        else:
            job_logger.warning("[SCHEDULER] Completed: Cleanup Sessions - FAILED")
    except Exception as e:
        job_logger.error(f"[SCHEDULER] Error in Cleanup Sessions: {e}")


def job_aggregate_daily_metrics():
    """
    Wrapper for aggregate_daily_metrics job.
    Handles imports and logging.
    """
    job_logger.info("[SCHEDULER] Starting: Aggregate Daily Metrics")
    try:
        from scripts.aggregate_daily_metrics import aggregate_daily_metrics
        result = aggregate_daily_metrics()  # Uses default (yesterday)
        if result:
            job_logger.info("[SCHEDULER] Completed: Aggregate Daily Metrics - SUCCESS")
        else:
            job_logger.warning("[SCHEDULER] Completed: Aggregate Daily Metrics - FAILED")
    except Exception as e:
        job_logger.error(f"[SCHEDULER] Error in Aggregate Daily Metrics: {e}")


def start_scheduler():
    """
    Initialize and start the background scheduler.
    
    This function is safe to call multiple times - it will only
    start the scheduler once.
    
    Returns:
        BackgroundScheduler: The scheduler instance
    """
    global _scheduler
    
    # Prevent double initialization
    if _scheduler is not None:
        job_logger.info("[SCHEDULER] Scheduler already running, skipping initialization")
        return _scheduler
    
    # Check if we should skip scheduler (e.g., during migrations)
    if os.environ.get('SKIP_SCHEDULER', '').lower() == 'true':
        job_logger.info("[SCHEDULER] SKIP_SCHEDULER=true, not starting scheduler")
        return None
    
    job_logger.info("[SCHEDULER] Initializing BackgroundScheduler...")
    
    # Create scheduler with job defaults
    _scheduler = BackgroundScheduler(
        job_defaults={
            'coalesce': True,      # Combine missed runs into one
            'max_instances': 1,     # Only one instance of each job at a time
            'misfire_grace_time': 300,  # 5 minutes grace period for misfired jobs
        },
        timezone='UTC'
    )
    
    # Add job: Aggregate Trip Interactions (hourly at minute 0)
    _scheduler.add_job(
        job_aggregate_interactions,
        CronTrigger(minute=0),  # Every hour at :00
        id='aggregate_trip_interactions',
        name='Aggregate Trip Interactions (Hourly)',
        replace_existing=True
    )
    job_logger.info("[SCHEDULER] Added job: Aggregate Trip Interactions (hourly at :00)")
    
    # Add job: Cleanup Sessions (every 15 minutes)
    _scheduler.add_job(
        job_cleanup_sessions,
        IntervalTrigger(minutes=15),  # Every 15 minutes
        id='cleanup_sessions',
        name='Cleanup Stale Sessions (Every 15 min)',
        replace_existing=True
    )
    job_logger.info("[SCHEDULER] Added job: Cleanup Sessions (every 15 minutes)")
    
    # Add job: Aggregate Daily Metrics (daily at 02:00 UTC)
    _scheduler.add_job(
        job_aggregate_daily_metrics,
        CronTrigger(hour=2, minute=0),  # Daily at 02:00 UTC
        id='aggregate_daily_metrics',
        name='Aggregate Daily Metrics (Daily 02:00 UTC)',
        replace_existing=True
    )
    job_logger.info("[SCHEDULER] Added job: Aggregate Daily Metrics (daily at 02:00 UTC)")
    
    # Start the scheduler
    _scheduler.start()
    job_logger.info("[SCHEDULER] BackgroundScheduler started successfully!")
    job_logger.info("[SCHEDULER] Scheduled jobs:")
    for job in _scheduler.get_jobs():
        job_logger.info(f"  - {job.name}: next run at {job.next_run_time}")
    
    return _scheduler


def stop_scheduler():
    """
    Stop the background scheduler gracefully.
    """
    global _scheduler
    
    if _scheduler is not None:
        job_logger.info("[SCHEDULER] Stopping BackgroundScheduler...")
        _scheduler.shutdown(wait=True)
        _scheduler = None
        job_logger.info("[SCHEDULER] BackgroundScheduler stopped.")


def get_scheduler_status():
    """
    Get the current status of the scheduler and its jobs.
    
    Returns:
        dict: Scheduler status information
    """
    global _scheduler
    
    if _scheduler is None:
        return {
            'running': False,
            'jobs': []
        }
    
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    
    return {
        'running': _scheduler.running,
        'jobs': jobs
    }


# For direct execution testing
if __name__ == '__main__':
    import time
    
    print("Testing BackgroundScheduler...")
    print("Press Ctrl+C to stop\n")
    
    scheduler = start_scheduler()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
            status = get_scheduler_status()
            print(f"\n[STATUS] Scheduler running: {status['running']}")
            for job in status['jobs']:
                print(f"  - {job['name']}: next at {job['next_run_time']}")
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping scheduler...")
        stop_scheduler()
        print("Done.")
