from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .database import create_db_and_tables
from .routers import feed_sources, feed_entries
from .jobs.fetch_feeds_job import fetch_feeds_job


# Worker
scheduler = BackgroundScheduler()


@scheduler.scheduled_job(CronTrigger.from_crontab("*/10 * * * *"))  # type: ignore[misc]
def scheduled_job() -> None:
    fetch_feeds_job()


# Web
app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    # TODO: Run migration script
    create_db_and_tables()
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    scheduler.shutdown()


app.include_router(feed_sources.router)
app.include_router(feed_entries.router)
