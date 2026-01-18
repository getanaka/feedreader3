from sqlmodel import Session
import pytest
from sqlalchemy.exc import IntegrityError
from psycopg.errors import UniqueViolation
from typing import cast

from feedreader3.models.feed_source import FeedSource


def test_feed_source_unique_constraint_name(session: Session) -> None:
    with pytest.raises(IntegrityError) as excinfo:
        feed_source1 = FeedSource(name="feed", feed_url="http://example.com/feed1.xml")
        feed_source2 = FeedSource(name="feed", feed_url="http://example.com/feed2.xml")
        session.add(feed_source1)
        session.add(feed_source2)
        session.commit()

    orig = cast(UniqueViolation, excinfo.value.orig)

    # PostgreSQL Error Code 23505: unique_violation
    # https://www.postgresql.org/docs/current/errcodes-appendix.html
    assert orig.sqlstate == "23505"
    assert "name" in str(orig.diag.constraint_name)


def test_feed_source_unique_constraint_url(session: Session) -> None:
    with pytest.raises(IntegrityError) as excinfo:
        feed_source1 = FeedSource(name="feed1", feed_url="http://example.com/feed.xml")
        feed_source2 = FeedSource(name="feed2", feed_url="http://example.com/feed.xml")
        session.add(feed_source1)
        session.add(feed_source2)
        session.commit()

    orig = cast(UniqueViolation, excinfo.value.orig)

    # PostgreSQL Error Code 23505: unique_violation
    # https://www.postgresql.org/docs/current/errcodes-appendix.html
    assert orig.sqlstate == "23505"
    assert "feed_url" in str(orig.diag.constraint_name)
