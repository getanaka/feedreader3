from sqlmodel import (
    Field,
    SQLModel,
    Relationship,
    UniqueConstraint,
)
from datetime import datetime
from .feed_source import FeedSource


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
