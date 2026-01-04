from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta

from feedreader3.models.feed_entry import FeedEntry
from feedreader3.models.feed_source import FeedSource


def test_read_feed_entries_no_entry(session: Session, client: TestClient) -> None:
    response = client.get("/feed-entries")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 0


def test_read_feed_entries_get_2(session: Session, client: TestClient) -> None:
    # FeedEntry requires a FeedSource due to the foreign key (FeedEntry.feed_source_id)
    feed_source = FeedSource(name="feed", feed_url="feed.rss")
    session.add(feed_source)
    session.commit()
    session.refresh(feed_source)

    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
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
    # FeedEntry requires a FeedSource due to the foreign key (FeedEntry.feed_source_id)
    feed_source = FeedSource(name="feed", feed_url="feed.rss")
    session.add(feed_source)
    session.commit()

    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=feed_source.id,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=feed_source.id,
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
    # FeedEntry requires a FeedSource due to the foreign key (FeedEntry.feed_source_id)
    feed_source = FeedSource(name="feed", feed_url="feed.rss")
    session.add(feed_source)
    session.commit()

    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=feed_source.id,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=feed_source.id,
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
    # FeedEntry requires a FeedSource due to the foreign key (FeedEntry.feed_source_id)
    feed_source = FeedSource(name="feed", feed_url="feed.rss")
    session.add(feed_source)
    session.commit()

    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=feed_source.id,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=feed_source.id,
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
    # FeedEntry requires a FeedSource due to the foreign key (FeedEntry.feed_source_id)
    feed_source = FeedSource(name="feed", feed_url="feed.rss")
    session.add(feed_source)
    session.commit()

    feed_entry0 = FeedEntry(
        first_seen_at=datetime(2025, 11, 1),
        feed_source_id=feed_source.id,
        entry_id="feed_entry0",
        entry_title="Feed Entry 0",
        entry_link="feed-entry0.html",
        entry_updated_at=datetime(2025, 11, 1),
    )
    feed_entry1 = FeedEntry(
        first_seen_at=datetime(2025, 11, 2),
        feed_source_id=feed_source.id,
        entry_id="feed_entry1",
        entry_title="Feed Entry 1",
        entry_link="feed-entry1.html",
        entry_updated_at=datetime(2025, 11, 2),
    )
    feed_entry2 = FeedEntry(
        first_seen_at=datetime(2025, 11, 3),
        feed_source_id=feed_source.id,
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
