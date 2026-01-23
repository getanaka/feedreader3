from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from .jobs.fetch_feeds_job import fetch_feeds_job
from datetime import timezone
import logging

logger = logging.getLogger(__name__)

_scheduler: BlockingScheduler | None = None


def get_scheduler() -> BlockingScheduler:
    if _scheduler is None:
        raise RuntimeError("_scheduler is None. Call initialize_scheduler()")
    return _scheduler


def initialize_scheduler(crontab_expr: str, misfire_grace_time: int) -> None:
    global _scheduler
    if _scheduler is not None:
        if _scheduler.running:
            # With BlockingScheduler, control never returns after start().
            # So this exception is never raised.
            raise RuntimeError(
                "_scheduler is running. BlockingScheduler cannot be reinitialized"
            )
        logger.warning("_scheduler has been already initialized. Reinitialize it")
        _scheduler = None

    _scheduler = BlockingScheduler()
    _scheduler.add_job(
        fetch_feeds_job,
        CronTrigger.from_crontab(crontab_expr, timezone.utc),
        misfire_grace_time=misfire_grace_time,
        coalesce=True,
    )


def startup_scheduler() -> None:
    get_scheduler().start()
