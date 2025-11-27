from typing import Annotated, Any, Generator
from fastapi import FastAPI, status, Depends, Query, HTTPException
from sqlmodel import (
    Field,
    Session,
    SQLModel,
    create_engine,
    select,
    Relationship,
    UniqueConstraint,
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import feedparser
from datetime import datetime


# DB
class FeedSourceBase(SQLModel):
    name: str = Field(index=True)
    feed_url: str = Field(index=True)


class FeedSource(FeedSourceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FeedSourcePublic(FeedSourceBase):
    id: int


class FeedSourceCreate(FeedSourceBase):
    pass


class FeedSourceUpdate(FeedSourceBase):
    name: str | None = None  # type: ignore[assignment]
    feed_url: str | None = None  # type: ignore[assignment]


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


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


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


@app.post(
    "/feed-sources",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedSourcePublic,
)
async def create_feed_source(feed_source: FeedSourceCreate, session: SessionDep) -> Any:
    db_feed_source = FeedSource.model_validate(feed_source)
    session.add(db_feed_source)
    session.commit()
    session.refresh(db_feed_source)
    return db_feed_source


@app.get("/feed-sources", response_model=list[FeedSourcePublic])
async def read_feed_sources(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Any:
    feed_sources = session.exec(select(FeedSource).offset(offset).limit(limit)).all()
    return feed_sources


@app.get("/feed-sources/{feed_source_id}", response_model=FeedSourcePublic)
async def read_feed_source(feed_source_id: int, session: SessionDep) -> FeedSource:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    return feed_source


@app.patch("/feed-sources/{feed_source_id}", response_model=FeedSourcePublic)
async def update_feed_source(
    feed_source_id: int, feed_source: FeedSourceUpdate, session: SessionDep
) -> Any:
    db_feed_source = session.get(FeedSource, feed_source_id)
    if not db_feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    feed_source_data = feed_source.model_dump(exclude_unset=True)
    db_feed_source.sqlmodel_update(feed_source_data)
    session.add(db_feed_source)
    session.commit()
    session.refresh(db_feed_source)
    return db_feed_source


@app.delete("/feed-sources/{feed_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed_source(feed_source_id: int, session: SessionDep) -> None:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    session.delete(feed_source)
    session.commit()
