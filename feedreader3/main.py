from typing import Annotated, Any, Generator
from fastapi import FastAPI, status, Depends, Query, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select


class FeedSourceBase(SQLModel):
    name: str = Field(index=True)
    feed_url: str = Field(index=True)


class FeedSource(FeedSourceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class FeedSourcePublic(FeedSourceBase):
    id: int


class FeedSourceCreate(FeedSourceBase):
    pass


class FeedSourceUpdate(FeedSourceBase):
    name: str | None = None  # type: ignore[assignment]
    feed_url: str | None = None  # type: ignore[assignment]


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

app = FastAPI()


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup() -> None:
    # TODO: Run migration script
    create_db_and_tables()


@app.post(
    "/feed-sources",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedSourcePublic,
)
async def create_feed_source(feed_source: FeedSourceCreate, session: SessionDep) -> Any:
    db_feed_source = FeedSource.model_validate(feed_source)
    session.add(db_feed_source)
    session.commit()
    session.refresh(db_feed_source)
    return db_feed_source


@app.get("/feed-sources", response_model=list[FeedSourcePublic])
async def read_feed_sources(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Any:
    feed_sources = session.exec(select(FeedSource).offset(offset).limit(limit)).all()
    return feed_sources


@app.get("/feed-sources/{feed_source_id}", response_model=FeedSourcePublic)
async def read_feed_source(feed_source_id: int, session: SessionDep) -> FeedSource:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    return feed_source


@app.patch("/feed-sources/{feed_source_id}", response_model=FeedSourcePublic)
async def update_feed_source(
    feed_source_id: int, feed_source: FeedSourceUpdate, session: SessionDep
) -> Any:
    db_feed_source = session.get(FeedSource, feed_source_id)
    if not db_feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    feed_source_data = feed_source.model_dump(exclude_unset=True)
    db_feed_source.sqlmodel_update(feed_source_data)
    session.add(db_feed_source)
    session.commit()
    session.refresh(db_feed_source)
    return db_feed_source


@app.delete("/feed-sources/{feed_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed_source(feed_source_id: int, session: SessionDep) -> None:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    session.delete(feed_source)
    session.commit()
