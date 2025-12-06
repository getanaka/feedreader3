from fastapi.testclient import TestClient
from sqlmodel import Session, select
import feedparser
from datetime import datetime, timedelta

from feedreader3.main import (
    FeedEntry,
    FeedEntryCreate,
    fetch_feeds,
)
from feedreader3.models.feed_source import FeedSource


def test_fetch_feeds_insert(session: Session) -> None:
    feed_source = FeedSource(name="test_feed", feed_url="tests/atom10.xml")
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
    feed_source = FeedSource(name="test_feed", feed_url="tests/atom10.xml")
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
    feed_source = FeedSource(name="test_feed", feed_url="tests/atom11.xml")
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
    feed_source = FeedSource(name="test_feed", feed_url="tests/atom12.xml")
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
    feed_source = FeedSource(name="test_feed", feed_url="tests/atom13.xml")
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


def test_read_feed_entries_no_entry(session: Session, client: TestClient) -> None:
    response = client.get("/feed-entries")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 0


def test_read_feed_entries_get_2(session: Session, client: TestClient) -> None:
    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=None,
    )
    session.add(feed_entry0)
    session.add(feed_entry1)
    session.commit()

    response = client.get("/feed-entries?order=asc")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2

    assert data[0]["id"] is not None
    assert data[0]["updated_at"] is not None
    assert (
        data[0]["first_seen_at"] == feed_entry0.first_seen_at.isoformat()
        if feed_entry0.first_seen_at is not None
        else data[0]["first_seen_at"] is None
    )
    assert data[0]["feed_source_id"] == feed_entry0.feed_source_id
    assert data[0]["entry_id"] == feed_entry0.entry_id
    assert data[0]["entry_title"] == feed_entry0.entry_title
    assert data[0]["entry_link"] == feed_entry0.entry_link
    assert (
        data[0]["entry_updated_at"] == feed_entry0.entry_updated_at.isoformat()
        if feed_entry0.entry_updated_at is not None
        else data[0]["entry_updated_at"] is None
    )

    assert data[1]["id"] is not None
    assert data[1]["updated_at"] is not None
    assert (
        data[1]["first_seen_at"] == feed_entry1.first_seen_at.isoformat()
        if feed_entry1.first_seen_at is not None
        else data[1]["first_seen_at"] is None
    )
    assert data[1]["feed_source_id"] == feed_entry1.feed_source_id
    assert data[1]["entry_id"] == feed_entry1.entry_id
    assert data[1]["entry_title"] == feed_entry1.entry_title
    assert data[1]["entry_link"] == feed_entry1.entry_link
    assert (
        data[1]["entry_updated_at"] == feed_entry1.entry_updated_at.isoformat()
        if feed_entry1.entry_updated_at is not None
        else data[1]["entry_updated_at"] is None
    )


def test_read_feed_entries_get_middle_1_from_3(
    session: Session, client: TestClient
) -> None:
    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=1,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=1,
        entry_id="feed_entry2",
        entry_title="Feed Entry 2",
        entry_link="feed-entry2.html",
        entry_updated_at=datetime(2025, 11, 3),
    )
    session.add(feed_entry0)
    session.add(feed_entry1)
    session.add(feed_entry2)
    session.commit()

    start = datetime(2025, 11, 2).isoformat()
    end = (datetime(2025, 11, 3) - timedelta(seconds=1)).isoformat()

    response = client.get(f"/feed-entries?start={start}&end={end}&order=asc")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] is not None
    assert data[0]["updated_at"] is not None
    assert (
        data[0]["first_seen_at"] == feed_entry1.first_seen_at.isoformat()
        if feed_entry1.first_seen_at is not None
        else data[0]["first_seen_at"] is None
    )
    assert data[0]["feed_source_id"] == feed_entry1.feed_source_id
    assert data[0]["entry_id"] == feed_entry1.entry_id
    assert data[0]["entry_title"] == feed_entry1.entry_title
    assert data[0]["entry_link"] == feed_entry1.entry_link
    assert (
        data[0]["entry_updated_at"] == feed_entry1.entry_updated_at.isoformat()
        if feed_entry1.entry_updated_at is not None
        else data[0]["entry_updated_at"] is None
    )


def test_read_feed_entries_get_latest_2_from_3(
    session: Session, client: TestClient
) -> None:
    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=1,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=1,
        entry_id="feed_entry2",
        entry_title="Feed Entry 2",
        entry_link="feed-entry2.html",
        entry_updated_at=datetime(2025, 11, 3),
    )
    session.add(feed_entry0)
    session.add(feed_entry1)
    session.add(feed_entry2)
    session.commit()

    start = datetime(2025, 11, 2).isoformat()

    response = client.get(f"/feed-entries?start={start}&order=asc")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] is not None
    assert data[0]["updated_at"] is not None
    assert (
        data[0]["first_seen_at"] == feed_entry1.first_seen_at.isoformat()
        if feed_entry1.first_seen_at is not None
        else data[0]["first_seen_at"] is None
    )
    assert data[0]["feed_source_id"] == feed_entry1.feed_source_id
    assert data[0]["entry_id"] == feed_entry1.entry_id
    assert data[0]["entry_title"] == feed_entry1.entry_title
    assert data[0]["entry_link"] == feed_entry1.entry_link
    assert (
        data[0]["entry_updated_at"] == feed_entry1.entry_updated_at.isoformat()
        if feed_entry1.entry_updated_at is not None
        else data[0]["entry_updated_at"] is None
    )

    assert data[1]["id"] is not None
    assert data[1]["updated_at"] is not None
    assert (
        data[1]["first_seen_at"] == feed_entry2.first_seen_at.isoformat()
        if feed_entry2.first_seen_at is not None
        else data[1]["first_seen_at"] is None
    )
    assert data[1]["feed_source_id"] == feed_entry2.feed_source_id
    assert data[1]["entry_id"] == feed_entry2.entry_id
    assert data[1]["entry_title"] == feed_entry2.entry_title
    assert data[1]["entry_link"] == feed_entry2.entry_link
    assert (
        data[1]["entry_updated_at"] == feed_entry2.entry_updated_at.isoformat()
        if feed_entry2.entry_updated_at is not None
        else data[1]["entry_updated_at"] is None
    )


def test_read_feed_entries_get_oldest_2_from_3(
    session: Session, client: TestClient
) -> None:
    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=1,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=1,
        entry_id="feed_entry2",
        entry_title="Feed Entry 2",
        entry_link="feed-entry2.html",
        entry_updated_at=datetime(2025, 11, 3),
    )
    session.add(feed_entry0)
    session.add(feed_entry1)
    session.add(feed_entry2)
    session.commit()

    end = (datetime(2025, 11, 3) - timedelta(seconds=1)).isoformat()

    response = client.get(f"/feed-entries?end={end}&order=asc")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] is not None
    assert data[0]["updated_at"] is not None
    assert (
        data[0]["first_seen_at"] == feed_entry0.first_seen_at.isoformat()
        if feed_entry0.first_seen_at is not None
        else data[0]["first_seen_at"] is None
    )
    assert data[0]["feed_source_id"] == feed_entry0.feed_source_id
    assert data[0]["entry_id"] == feed_entry0.entry_id
    assert data[0]["entry_title"] == feed_entry0.entry_title
    assert data[0]["entry_link"] == feed_entry0.entry_link
    assert (
        data[0]["entry_updated_at"] == feed_entry0.entry_updated_at.isoformat()
        if feed_entry0.entry_updated_at is not None
        else data[0]["entry_updated_at"] is None
    )

    assert data[1]["id"] is not None
    assert data[1]["updated_at"] is not None
    assert (
        data[1]["first_seen_at"] == feed_entry1.first_seen_at.isoformat()
        if feed_entry1.first_seen_at is not None
        else data[1]["first_seen_at"] is None
    )
    assert data[1]["feed_source_id"] == feed_entry1.feed_source_id
    assert data[1]["entry_id"] == feed_entry1.entry_id
    assert data[1]["entry_title"] == feed_entry1.entry_title
    assert data[1]["entry_link"] == feed_entry1.entry_link
    assert (
        data[1]["entry_updated_at"] == feed_entry1.entry_updated_at.isoformat()
        if feed_entry1.entry_updated_at is not None
        else data[1]["entry_updated_at"] is None
    )


def test_read_feed_entries_get_3_desc(session: Session, client: TestClient) -> None:
    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=1,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=1,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=1,
        entry_id="feed_entry2",
        entry_title="Feed Entry 2",
        entry_link="feed-entry2.html",
        entry_updated_at=datetime(2025, 11, 3),
    )
    session.add(feed_entry0)
    session.add(feed_entry1)
    session.add(feed_entry2)
    session.commit()

    response = client.get("/feed-entries?order=desc")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 3

    assert data[0]["id"] is not None
    assert data[0]["updated_at"] is not None
    assert (
        data[0]["first_seen_at"] == feed_entry2.first_seen_at.isoformat()
        if feed_entry2.first_seen_at is not None
        else data[0]["first_seen_at"] is None
    )
    assert data[0]["feed_source_id"] == feed_entry2.feed_source_id
    assert data[0]["entry_id"] == feed_entry2.entry_id
    assert data[0]["entry_title"] == feed_entry2.entry_title
    assert data[0]["entry_link"] == feed_entry2.entry_link
    assert (
        data[0]["entry_updated_at"] == feed_entry2.entry_updated_at.isoformat()
        if feed_entry2.entry_updated_at is not None
        else data[0]["entry_updated_at"] is None
    )

    assert data[1]["id"] is not None
    assert data[1]["updated_at"] is not None
    assert (
        data[1]["first_seen_at"] == feed_entry1.first_seen_at.isoformat()
        if feed_entry1.first_seen_at is not None
        else data[1]["first_seen_at"] is None
    )
    assert data[1]["feed_source_id"] == feed_entry1.feed_source_id
    assert data[1]["entry_id"] == feed_entry1.entry_id
    assert data[1]["entry_title"] == feed_entry1.entry_title
    assert data[1]["entry_link"] == feed_entry1.entry_link
    assert (
        data[1]["entry_updated_at"] == feed_entry1.entry_updated_at.isoformat()
        if feed_entry1.entry_updated_at is not None
        else data[1]["entry_updated_at"] is None
    )

    assert data[2]["id"] is not None
    assert data[2]["updated_at"] is not None
    assert (
        data[2]["first_seen_at"] == feed_entry0.first_seen_at.isoformat()
        if feed_entry0.first_seen_at is not None
        else data[2]["first_seen_at"] is None
    )
    assert data[2]["feed_source_id"] == feed_entry0.feed_source_id
    assert data[2]["entry_id"] == feed_entry0.entry_id
    assert data[2]["entry_title"] == feed_entry0.entry_title
    assert data[2]["entry_link"] == feed_entry0.entry_link
    assert (
        data[2]["entry_updated_at"] == feed_entry0.entry_updated_at.isoformat()
        if feed_entry0.entry_updated_at is not None
        else data[2]["entry_updated_at"] is None
    )
