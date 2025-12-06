from typing import Annotated, Sequence, Literal, cast
from fastapi import FastAPI, Query
from sqlmodel import (
    Field,
    Session,
    SQLModel,
    select,
    Relationship,
    UniqueConstraint,
    func,
    Column,
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import feedparser
from datetime import datetime
from .database import engine, create_db_and_tables
from .dependencies import SessionDep
from .models.feed_source import FeedSource
from .routers import feed_sources


# DB
class FeedEntryBase(SQLModel):
    feed_source_id: int = Field(foreign_key="feedsource.id")
    entry_id: str
    entry_title: str
    entry_link: str
    entry_updated_at: datetime | None = Field(default=None)


class FeedEntry(FeedEntryBase, table=True):
    __table_args__ = ((UniqueConstraint("feed_source_id", "entry_id")),)

    id: int | None = Field(default=None, primary_key=True)
    updated_at: datetime | None = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    first_seen_at: datetime | None

    feed_source: FeedSource = Relationship()


class FeedEntryCreate(FeedEntryBase):
    first_seen_at: datetime


class FeedEntryUpdate(SQLModel):
    entry_title: str | None
    entry_link: str | None
    entry_updated_at: datetime | None


# Worker
scheduler = BackgroundScheduler()


@scheduler.scheduled_job(CronTrigger.from_crontab("*/10 * * * *"))  # type: ignore[misc]
def scheduled_job() -> None:
    print("[scheduled_job] Start")
    with Session(engine) as session:
        fetch_feeds(session)
    print("[scheduled_job] Done")


def fetch_feeds(session: Session) -> None:
    feed_sources = session.exec(select(FeedSource)).all()
    for feed_source in feed_sources:
        parsed_feed = feedparser.parse(feed_source.feed_url)
        if parsed_feed.entries is not None:
            store_feed_entries(session, feed_source, parsed_feed.entries)


def store_feed_entries(
    session: Session,
    feed_source: FeedSource,
    parsed_entries: list[feedparser.util.FeedParserDict],
) -> None:
    for parsed_entry in parsed_entries:
        if parsed_entry.get("link") is None:
            continue

        entry_id = parsed_entry.get("id") or parsed_entry.get("link")
        if entry_id is None:
            continue

        if parsed_entry.get("updated_parsed") is not None:
            # feedparser returns UTC datetime
            entry_updated_at = datetime(*parsed_entry.updated_parsed[:6])
        else:
            entry_updated_at = None

        entry_title = parsed_entry.get("title", "")

        db_feed_entry = session.exec(
            select(FeedEntry).where(
                FeedEntry.feed_source_id == feed_source.id,
                FeedEntry.entry_id == entry_id,
            )
        ).one_or_none()
        # Insert new entry
        if db_feed_entry is None:
            feed_entry_create = FeedEntryCreate(
                first_seen_at=datetime.now(),
                feed_source_id=feed_source.id,
                entry_id=entry_id,
                entry_title=entry_title,
                entry_link=parsed_entry.link,
                entry_updated_at=entry_updated_at,
            )
            db_feed_entry = FeedEntry.model_validate(feed_entry_create)
            session.add(db_feed_entry)
        # Update the entry
        else:
            feed_entry_update = FeedEntryUpdate(
                entry_title=entry_title,
                entry_link=parsed_entry.link,
                entry_updated_at=entry_updated_at,
            )
            dump = feed_entry_update.model_dump(exclude_unset=True)
            db_feed_entry.sqlmodel_update(dump)

    session.commit()


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


@app.get("/feed-entries")
async def read_feed_entries(
    session: SessionDep,
    start: datetime = datetime.min,
    end: datetime = datetime.max,
    order: Literal["asc", "desc"] = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[FeedEntry]:
    ts = func.coalesce(FeedEntry.entry_updated_at, FeedEntry.first_seen_at)
    ts_order = ts.asc() if order == "asc" else ts.desc()
    id_col = cast(Column[int], FeedEntry.id)
    id_order = id_col.asc() if order == "asc" else id_col.desc()
    feed_entries = session.exec(
        select(FeedEntry)
        .where(start <= ts, ts <= end)
        .order_by(ts_order, id_order)
        .offset(offset)
        .limit(limit)
    ).all()
    return feed_entries
