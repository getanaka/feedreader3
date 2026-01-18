from sqlmodel import Field, SQLModel
from pydantic import AnyUrl, AnyHttpUrl, field_validator
from typing import Any


def convert_url(url: Any) -> Any:
    if isinstance(url, AnyUrl):
        return str(url)
    else:
        return url


class FeedSourceBase(SQLModel):
    name: str = Field(index=True, unique=True)
    feed_url: str = Field(index=True, unique=True)

    @field_validator("feed_url", mode="before")
    @classmethod
    def convert_feed_url(cls, value: Any) -> Any:
        return convert_url(value)


class FeedSource(FeedSourceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FeedSourcePublic(FeedSourceBase):
    id: int


class FeedSourceCreate(SQLModel):
    name: str
    feed_url: AnyHttpUrl


class FeedSourceUpdate(SQLModel):
    name: str | None = None
    feed_url: AnyHttpUrl | None = None
