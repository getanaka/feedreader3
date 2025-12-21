from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .database import initialize_engine, finalize_engine
from .routers import feed_sources, feed_entries
from .scheduler import (
    initialize_scheduler,
    startup_scheduler,
    shutdown_scheduler,
    finalize_scheduler,
)
from .settings import initialize_settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # settings
    initialize_settings()
    settings = get_settings()
    print(settings.scheduler_crontab_expr)
    print(settings.scheduler_misfire_grace_time)

    # DB
    initialize_engine(settings.database_file_name)

    # scheduler
    initialize_scheduler(
        settings.scheduler_crontab_expr, settings.scheduler_misfire_grace_time
    )
    startup_scheduler()

    yield

    # scheduler
    shutdown_scheduler()
    finalize_scheduler()

    finalize_engine()


app = FastAPI(lifespan=lifespan)

app.include_router(feed_sources.router)
app.include_router(feed_entries.router)
