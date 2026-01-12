from sqlmodel import Session, select
import feedparser
from datetime import datetime, timezone
from ..database import get_engine
from ..models.feed_source import FeedSource
from ..models.feed_entry import FeedEntry, FeedEntryUpdate, FeedEntryCreate
import logging

logger = logging.getLogger("uvicorn." + __name__)


def fetch_feeds_job() -> None:
    logger.info("start fetch_feed_job")
    with Session(get_engine()) as session:
        fetch_feeds(session)
    logger.info("end fetch_feed_job")


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
            entry_updated_at = datetime(
                parsed_entry.updated_parsed[0],
                parsed_entry.updated_parsed[1],
                parsed_entry.updated_parsed[2],
                parsed_entry.updated_parsed[3],
                parsed_entry.updated_parsed[4],
                parsed_entry.updated_parsed[5],
                tzinfo=timezone.utc,
            )
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
                first_seen_at=datetime.now(timezone.utc),
                feed_source_id=feed_source.id,
                entry_id=entry_id,
                entry_title=entry_title,
                entry_link=parsed_entry.link,
                entry_updated_at=entry_updated_at,
            )
            db_feed_entry = FeedEntry.model_validate(feed_entry_create)
            session.add(db_feed_entry)
            logger.info(f"Source: {feed_source.name}, New entry: {entry_title}")
        # Update the entry
        else:
            feed_entry_update = FeedEntryUpdate(
                entry_title=entry_title,
                entry_link=parsed_entry.link,
                entry_updated_at=entry_updated_at,
            )
            dump = feed_entry_update.model_dump(exclude_unset=True)
            db_feed_entry.sqlmodel_update(dump)
            logger.info(f"Source: {feed_source.name}, Updated entry: {entry_title}")

    session.commit()
