from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .database import create_db_and_tables
from .routers import feed_sources, feed_entries
from .scheduler import background_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # TODO: Run migration script
    create_db_and_tables()
    background_scheduler.start()
    yield
    background_scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(feed_sources.router)
app.include_router(feed_entries.router)
