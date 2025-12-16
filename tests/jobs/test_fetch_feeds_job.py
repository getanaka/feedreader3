from pytest import MonkeyPatch
from sqlmodel import Session, select
import feedparser
from datetime import datetime, tzinfo, timezone
from typing import Self

from feedreader3.jobs import fetch_feeds_job
from feedreader3.jobs.fetch_feeds_job import fetch_feeds, store_feed_entries
from feedreader3.models.feed_source import FeedSource
from feedreader3.models.feed_entry import FeedEntry, FeedEntryCreate


def test_fetch_feeds_insert(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom10.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    parsed_feed = feedparser.parse(feed_source.feed_url)
    parsed_entry = parsed_feed.entries[0]

    fetch_feeds(session)

    results = session.exec(
        select(FeedEntry).where(FeedEntry.feed_source_id == feed_source.id)
    ).all()
    assert len(results) == 1
    assert results[0].id is not None
    assert results[0].updated_at is not None
    assert results[0].first_seen_at is not None
    assert results[0].feed_source_id == feed_source.id
    assert results[0].entry_id == parsed_entry.id
    assert results[0].entry_title == parsed_entry.title
    assert results[0].entry_link == parsed_entry.link
    # SQLite cannot have timezone so we need to compare datetime without tzinfo.
    assert results[0].entry_updated_at == datetime(*parsed_entry.updated_parsed[:6])


def test_fetch_feeds_update(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom10.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    feed_entry_create = FeedEntryCreate(
        first_seen_at=datetime.now(),
        feed_source_id=feed_source.id,
        entry_id="tag:feedparser.org,2005-11-09:/docs/examples/atom10.xml:3",
        entry_title="",
        entry_link="",
        entry_updated_at=datetime.min,
    )
    db_feed_entry = FeedEntry.model_validate(feed_entry_create)
    session.add(db_feed_entry)
    session.commit()

    parsed_feed = feedparser.parse(feed_source.feed_url)
    parsed_entry = parsed_feed.entries[0]

    fetch_feeds(session)

    results = session.exec(
        select(FeedEntry).where(FeedEntry.feed_source_id == feed_source.id)
    ).all()
    assert len(results) == 1
    assert results[0].id is not None
    assert results[0].updated_at is not None
    assert results[0].first_seen_at is not None
    assert results[0].feed_source_id == feed_source.id
    assert results[0].entry_id == feed_entry_create.entry_id
    assert results[0].entry_id == parsed_entry.id
    assert results[0].entry_title == parsed_entry.title
    assert results[0].entry_link == parsed_entry.link
    # SQLite cannot have timezone so we need to compare datetime without tzinfo.
    assert results[0].entry_updated_at == datetime(*parsed_entry.updated_parsed[:6])


def test_fetch_feeds_add_atom_without_published(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom11.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    parsed_feed = feedparser.parse(feed_source.feed_url)
    parsed_entry = parsed_feed.entries[0]

    fetch_feeds(session)

    results = session.exec(
        select(FeedEntry).where(FeedEntry.feed_source_id == feed_source.id)
    ).all()
    assert len(results) == 1
    assert results[0].id is not None
    assert results[0].updated_at is not None
    assert results[0].first_seen_at is not None
    assert results[0].feed_source_id == feed_source.id
    assert results[0].entry_id == parsed_entry.id
    assert results[0].entry_title == parsed_entry.title
    assert results[0].entry_link == parsed_entry.link
    # SQLite cannot have timezone so we need to compare datetime without tzinfo.
    assert results[0].entry_updated_at == datetime(*parsed_entry.updated_parsed[:6])


def test_fetch_feeds_add_atom_without_published_and_updated(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom12.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    parsed_feed = feedparser.parse(feed_source.feed_url)
    parsed_entry = parsed_feed.entries[0]

    fetch_feeds(session)

    results = session.exec(
        select(FeedEntry).where(FeedEntry.feed_source_id == feed_source.id)
    ).all()
    assert len(results) == 1
    assert results[0].id is not None
    assert results[0].updated_at is not None
    assert results[0].first_seen_at is not None
    assert results[0].feed_source_id == feed_source.id
    assert results[0].entry_id == parsed_entry.id
    assert results[0].entry_title == parsed_entry.title
    assert results[0].entry_link == parsed_entry.link
    # SQLite cannot have timezone so we need to compare datetime without tzinfo.
    assert results[0].entry_updated_at is None


def test_fetch_feeds_add_atom_has_duplicated_id_entries(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom13.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    parsed_feed = feedparser.parse(feed_source.feed_url)
    parsed_entry = parsed_feed.entries[1]

    fetch_feeds(session)

    results = session.exec(
        select(FeedEntry).where(FeedEntry.feed_source_id == feed_source.id)
    ).all()
    assert len(results) == 1
    assert results[0].id is not None
    assert results[0].updated_at is not None
    assert results[0].first_seen_at is not None
    assert results[0].feed_source_id == feed_source.id
    assert results[0].entry_id == parsed_entry.id
    assert results[0].entry_title == parsed_entry.title
    assert results[0].entry_link == parsed_entry.link
    # SQLite cannot have timezone so we need to compare datetime without tzinfo.
    assert results[0].entry_updated_at == datetime(*parsed_entry.updated_parsed[:6])


def test_store_feed_entries_first_seen_at_timezone(
    session: Session, monkeypatch: MonkeyPatch
) -> None:
    has_called = {"value": False}

    class MockDateTime(datetime):
        @classmethod
        def now(cls: type[Self], tz: tzinfo | None = None) -> Self:
            assert tz is timezone.utc
            has_called["value"] = True
            return cls(1970, 1, 1, tzinfo=tz)

    monkeypatch.setattr(fetch_feeds_job, "datetime", MockDateTime)

    feed_source = FeedSource(name="test_feed", feed_url="tests/jobs/atom14.xml")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    parsed_entries = feedparser.parse(feed_source.feed_url).entries

    store_feed_entries(session, feed_source, parsed_entries)

    results = session.exec(select(FeedEntry)).all()

    assert has_called["value"]
    # SQLite stores naive datetime
    assert results[0].first_seen_at == MockDateTime(1970, 1, 1)
