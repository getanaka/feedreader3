from feedreader3.scheduler import background_scheduler


def test_fetch_job_scheduler_configuration() -> None:
    jobs = background_scheduler.get_jobs()

    fetch_job = None
    for job in jobs:
        if job.name == "scheduled_job":
            fetch_job = job
            break

    assert fetch_job is not None
    assert fetch_job.misfire_grace_time == 30
    assert fetch_job.coalesce is True
