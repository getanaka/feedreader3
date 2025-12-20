from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs.fetch_feeds_job import fetch_feeds_job
from datetime import timezone

_background_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    if _background_scheduler is None:
        raise RuntimeError("_background_scheduler is None. Call initialize_scheduler()")
    return _background_scheduler


def initialize_scheduler(crontab_expr: str, misfire_grace_time: int) -> None:
    global _background_scheduler
    if _background_scheduler is not None:
        raise RuntimeError(
            "_background_scheduler is not None. Call finalize_scheduler() before initialization"
        )

    _background_scheduler = BackgroundScheduler()
    _background_scheduler.add_job(
        fetch_feeds_job,
        CronTrigger.from_crontab(crontab_expr, timezone.utc),
        misfire_grace_time=misfire_grace_time,
        coalesce=True,
    )


def finalize_scheduler() -> None:
    global _background_scheduler
    if _background_scheduler is None:
        raise RuntimeError("_background_scheduler is None. Call initialize_scheduler()")
    elif _background_scheduler.running:
        raise RuntimeError(
            "_background_scheduler is running. Call shutdown_scheduler() before finalization"
        )

    _background_scheduler = None


def startup_scheduler() -> None:
    get_scheduler().start()


def shutdown_scheduler() -> None:
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown()
