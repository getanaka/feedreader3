from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .database import initialize_engine, finalize_engine
from .routers import health, feed_sources, feed_entries
from .settings import initialize_settings
from .exception_handlers import global_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # settings
    initialize_settings()

    # DB
    initialize_engine()

    yield

    finalize_engine()


app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(feed_sources.router)
app.include_router(feed_entries.router)

app.add_exception_handler(Exception, global_exception_handler)
