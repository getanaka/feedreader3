import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
import feedparser
from datetime import datetime

from feedreader3.main import (
    FeedSource,
    FeedEntry,
    FeedEntryCreate,
    app,
    get_session,
    fetch_feeds,
)


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_feed_source(client: TestClient) -> None:
    response = client.post(
        "/feed-sources/", json={"name": "feed_01", "feed_url": "feed-01.rss"}
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "feed_01"
    assert data["feed_url"] == "feed-01.rss"
    assert data["id"] is not None


def test_create_feed_source_incomplete(client: TestClient) -> None:
    response = client.post("/feed-sources/", json={"name": "feed_02"})

    assert response.status_code == 422


def test_create_feed_source_invalid(client: TestClient) -> None:
    response = client.post("/feed-sources/", json={"name": "feed_02", "feed_url": 100})

    assert response.status_code == 422


def test_read_feed_sources(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="feed_01", feed_url="feed-01.rss")
    feed_source1 = FeedSource(name="feed_02", feed_url="feed-02.rss")
    session.add(feed_source0)
    session.add(feed_source1)
    session.commit()

    response = client.get("/feed-sources/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == feed_source0.name
    assert data[0]["feed_url"] == feed_source0.feed_url
    assert data[0]["id"] == feed_source0.id
    assert data[1]["name"] == feed_source1.name
    assert data[1]["feed_url"] == feed_source1.feed_url
    assert data[1]["id"] == feed_source1.id


def test_read_feed_source(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="feed_01", feed_url="feed-01.rss")
    session.add(feed_source0)
    session.commit()

    response = client.get(f"/feed-sources/{feed_source0.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == feed_source0.name
    assert data["feed_url"] == feed_source0.feed_url
    assert data["id"] == feed_source0.id


def test_update_feed_source(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="feed_01", feed_url="feed-01.rss")
    session.add(feed_source0)
    session.commit()

    response = client.patch(
        f"/feed-sources/{feed_source0.id}", json={"name": "feed_02"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "feed_02"
    assert data["feed_url"] == feed_source0.feed_url
    assert data["id"] == feed_source0.id


def test_delete_feed_source(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="feed_01", feed_url="feed-01.rss")
    session.add(feed_source0)
    session.commit()

    response = client.delete(f"/feed-sources/{feed_source0.id}")

    db_feed_source0 = session.get(FeedSource, feed_source0.id)

    assert response.status_code == 204
    assert db_feed_source0 is None


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
