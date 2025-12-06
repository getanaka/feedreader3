from typing import Annotated, Any
from fastapi import status, Query, HTTPException, APIRouter
from sqlmodel import select
from ..models.feed_source import (
    FeedSource,
    FeedSourcePublic,
    FeedSourceCreate,
    FeedSourceUpdate,
)
from ..dependencies import SessionDep

router = APIRouter(prefix="/feed-sources")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedSourcePublic,
)
async def create_feed_source(feed_source: FeedSourceCreate, session: SessionDep) -> Any:
    db_feed_source = FeedSource.model_validate(feed_source)
    session.add(db_feed_source)
    session.commit()
    session.refresh(db_feed_source)
    return db_feed_source


@router.get("", response_model=list[FeedSourcePublic])
async def read_feed_sources(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Any:
    feed_sources = session.exec(select(FeedSource).offset(offset).limit(limit)).all()
    return feed_sources


@router.get("/{feed_source_id}", response_model=FeedSourcePublic)
async def read_feed_source(feed_source_id: int, session: SessionDep) -> FeedSource:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    return feed_source


@router.patch("/{feed_source_id}", response_model=FeedSourcePublic)
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


@router.delete("/{feed_source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feed_source(feed_source_id: int, session: SessionDep) -> None:
    feed_source = session.get(FeedSource, feed_source_id)
    if not feed_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feed source not found"
        )
    session.delete(feed_source)
    session.commit()
