from fastapi.testclient import TestClient
from sqlmodel import Session
from feedreader3.models.feed_source import FeedSource


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


def test_create_feed_source_duplicate_name(
    session: Session, client: TestClient
) -> None:
    name = "name"

    feed_source = FeedSource(name=name, feed_url="feed-url-0.rss")
    session.add(feed_source)
    session.commit()

    response = client.post(
        "/feed-sources", json={"name": name, "feed_url": "feed-url-1.rss"}
    )
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "name"
    assert data["detail"]["message"] == "already exists"


def test_create_feed_source_duplicate_url(session: Session, client: TestClient) -> None:
    feed_url = "source_url"

    feed_source = FeedSource(name="name0", feed_url=feed_url)
    session.add(feed_source)
    session.commit()

    response = client.post(
        "/feed-sources", json={"name": "name1", "feed_url": feed_url}
    )
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "feed_url"
    assert data["detail"]["message"] == "already exists"


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


def test_update_feed_source_duplicate_name(
    session: Session, client: TestClient
) -> None:
    feed_source0 = FeedSource(name="name0", feed_url="feed-url-0.rss")
    feed_source1 = FeedSource(name="name1", feed_url="feed-url-1.rss")
    session.add(feed_source0)
    session.add(feed_source1)
    session.commit()

    name = "name1"

    response = client.patch(f"/feed-sources/{feed_source0.id}", json={"name": name})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "name"
    assert data["detail"]["message"] == "already exists"


def test_update_feed_source_duplicate_url(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="name0", feed_url="feed-url-0.rss")
    feed_source1 = FeedSource(name="name1", feed_url="feed-url-1.rss")
    session.add(feed_source0)
    session.add(feed_source1)
    session.commit()

    url = "feed-url-1.rss"

    response = client.patch(f"/feed-sources/{feed_source0.id}", json={"feed_url": url})
    data = response.json()

    assert response.status_code == 409
    assert data["detail"]["field"] == "feed_url"
    assert data["detail"]["message"] == "already exists"


def test_delete_feed_source(session: Session, client: TestClient) -> None:
    feed_source0 = FeedSource(name="feed_01", feed_url="feed-01.rss")
    session.add(feed_source0)
    session.commit()
    feed_source0_id = feed_source0.id

    response = client.delete(f"/feed-sources/{feed_source0_id}")
    session.expire_all()

    db_feed_source0 = session.get(FeedSource, feed_source0_id)

    assert response.status_code == 204
    assert db_feed_source0 is None
