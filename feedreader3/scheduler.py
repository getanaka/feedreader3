from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs.fetch_feeds_job import fetch_feeds_job

background_scheduler = BackgroundScheduler()


@background_scheduler.scheduled_job(
    CronTrigger.from_crontab("*/10 * * * *"), misfire_grace_time=30, coalesce=True
)  # type: ignore[misc]
def scheduled_job() -> None:
    fetch_feeds_job()
