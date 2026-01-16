from sqlmodel import Field, SQLModel


class FeedSourceBase(SQLModel):
    name: str = Field(index=True, unique=True)
    feed_url: str = Field(index=True, unique=True)


class FeedSource(FeedSourceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FeedSourcePublic(FeedSourceBase):
    id: int


class FeedSourceCreate(FeedSourceBase):
    pass


class FeedSourceUpdate(SQLModel):
    name: str | None = None
    feed_url: str | None = None
