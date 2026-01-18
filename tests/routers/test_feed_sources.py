from fastapi.testclient import TestClient
from sqlmodel import Session
from feedreader3.models.feed_source import FeedSource


def test_create_feed_source(client: TestClient) -> None:
    name = "feed"
    feed_url = "http://example.com/feed.xml"

    response = client.post(
        "/feed-sources",
        json={"name": name, "feed_url": feed_url},
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == name
    assert data["feed_url"] == feed_url
    assert data["id"] is not None


def test_create_feed_source_incomplete(client: TestClient) -> None:
    response = client.post("/feed-sources", json={"name": "feed"})

    assert response.status_code == 422


def test_create_feed_source_invalid(client: TestClient) -> None:
    response = client.post("/feed-sources", json={"name": "feed", "feed_url": 100})

    assert response.status_code == 422


def test_create_feed_source_duplicate_name(
    session: Session, client: TestClient
) -> None:
    name = "feed"

    feed_source = FeedSource(name=name, feed_url="http://example.com/feed1.xml")
    session.add(feed_source)
    session.commit()

    response = client.post(
        "/feed-sources",
        json={"name": name, "feed_url": "http://example.com/feed2.xml"},
    )
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "name"
    assert data["detail"]["message"] == "already exists"


def test_create_feed_source_duplicate_url(session: Session, client: TestClient) -> None:
    feed_url = "http://example.com/feed.xml"

    feed_source = FeedSource(name="feed", feed_url=feed_url)
    session.add(feed_source)
    session.commit()

    response = client.post(
        "/feed-sources", json={"name": "feed2", "feed_url": feed_url}
    )
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "feed_url"
    assert data["detail"]["message"] == "already exists"


def test_read_feed_sources(session: Session, client: TestClient) -> None:
    feed_source1 = FeedSource(name="feed1", feed_url="http://example.com/feed1.xml")
    feed_source2 = FeedSource(name="feed2", feed_url="http://example.com/feed2.xml")
    session.add(feed_source1)
    session.add(feed_source2)
    session.commit()

    response = client.get("/feed-sources")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["name"] == feed_source1.name
    assert data[0]["feed_url"] == feed_source1.feed_url
    assert data[0]["id"] == feed_source1.id
    assert data[1]["name"] == feed_source2.name
    assert data[1]["feed_url"] == feed_source2.feed_url
    assert data[1]["id"] == feed_source2.id


def test_read_feed_source(session: Session, client: TestClient) -> None:
    feed_source = FeedSource(name="feed", feed_url="http://example.com/feed.xml")
    session.add(feed_source)
    session.commit()

    response = client.get(f"/feed-sources/{feed_source.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == feed_source.name
    assert data["feed_url"] == feed_source.feed_url
    assert data["id"] == feed_source.id


def test_update_feed_source(session: Session, client: TestClient) -> None:
    feed_source = FeedSource(name="feed1", feed_url="http://example.com/feed.xml")
    session.add(feed_source)
    session.commit()

    response = client.patch(f"/feed-sources/{feed_source.id}", json={"name": "feed2"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "feed2"
    assert data["feed_url"] == feed_source.feed_url
    assert data["id"] == feed_source.id


def test_update_feed_source_duplicate_name(
    session: Session, client: TestClient
) -> None:
    feed_source1 = FeedSource(name="feed1", feed_url="http://example.com/feed1.xml")
    feed_source2 = FeedSource(name="feed2", feed_url="http://example.com/feed2.xml")
    session.add(feed_source1)
    session.add(feed_source2)
    session.commit()

    name = "feed2"

    response = client.patch(f"/feed-sources/{feed_source1.id}", json={"name": name})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "name"
    assert data["detail"]["message"] == "already exists"


def test_update_feed_source_duplicate_url(session: Session, client: TestClient) -> None:
    feed_source1 = FeedSource(name="feed1", feed_url="http://example.com/feed1.xml")
    feed_source2 = FeedSource(name="feed2", feed_url="http://example.com/feed2.xml")
    session.add(feed_source1)
    session.add(feed_source2)
    session.commit()

    feed_url = "http://example.com/feed2.xml"

    response = client.patch(
        f"/feed-sources/{feed_source1.id}", json={"feed_url": feed_url}
    )
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "feed_url"
    assert data["detail"]["message"] == "already exists"


def test_delete_feed_source(session: Session, client: TestClient) -> None:
    feed_source = FeedSource(name="feed", feed_url="http://example.com/feed.xml")
    session.add(feed_source)
    session.commit()
    feed_source_id = feed_source.id

    response = client.delete(f"/feed-sources/{feed_source_id}")
    session.expire_all()

    db_feed_source = session.get(FeedSource, feed_source_id)

    assert response.status_code == 204
    assert db_feed_source is None
