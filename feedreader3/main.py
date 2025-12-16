from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import feed_sources, feed_entries
from .scheduler import background_scheduler

# Web
app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    # TODO: Run migration script
    create_db_and_tables()
    background_scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    background_scheduler.shutdown()


app.include_router(feed_sources.router)
app.include_router(feed_entries.router)
