import pytest
from typing import Generator
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import timezone

from feedreader3.scheduler import (
    initialize_scheduler,
    get_scheduler,
    finalize_scheduler,
)

CRONTAB_EXPR = "*/10 * * * *"
MISFIRE_GRACE_TIME = 30


@pytest.fixture(name="scheduler")
def scheduler_fixture() -> Generator[BackgroundScheduler, None, None]:
    initialize_scheduler(CRONTAB_EXPR, MISFIRE_GRACE_TIME)
    try:
        yield get_scheduler()
    finally:
        finalize_scheduler()


def test_fetch_job_scheduler_configuration(scheduler: BackgroundScheduler) -> None:
    jobs = scheduler.get_jobs()

    fetch_job = None
    for job in jobs:
        if job.name == "fetch_feeds_job":
            fetch_job = job
            break

    assert fetch_job is not None
    assert (
        fetch_job.trigger.__getstate__()
        == CronTrigger.from_crontab(CRONTAB_EXPR, timezone.utc).__getstate__()
    )
    assert fetch_job.misfire_grace_time == MISFIRE_GRACE_TIME
    assert fetch_job.coalesce is True
