from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    UniqueConstraint,
    DateTime,
    Column,
)
from datetime import datetime, timezone
from .feed_source import FeedSource


class FeedEntryBase(SQLModel):
    feed_source_id: int = Field(foreign_key="feedsource.id", ondelete="CASCADE")
    entry_id: str
    entry_title: str
    entry_link: str
    entry_updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class FeedEntry(FeedEntryBase, table=True):
    __table_args__ = ((UniqueConstraint("feed_source_id", "entry_id")),)

    id: int | None = Field(default=None, primary_key=True)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )
    first_seen_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    feed_source: FeedSource = Relationship(back_populates="feed_entries")


class FeedEntryCreate(FeedEntryBase):
    first_seen_at: datetime


class FeedEntryUpdate(SQLModel):
    entry_title: str | None
    entry_link: str | None
    entry_updated_at: datetime | None
