from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .database import create_db_and_tables
from .routers import feed_sources, feed_entries
from .scheduler import (
    initialize_scheduler,
    startup_scheduler,
    shutdown_scheduler,
    finalize_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # TODO: Run migration script
    create_db_and_tables()
    initialize_scheduler("*/10 * * * *", 30)
    startup_scheduler()
    yield
    shutdown_scheduler()
    finalize_scheduler()


app = FastAPI(lifespan=lifespan)

app.include_router(feed_sources.router)
app.include_router(feed_entries.router)
