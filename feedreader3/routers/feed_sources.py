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
from sqlalchemy.exc import IntegrityError as SqlAlchemyIntegrityError
from psycopg.errors import IntegrityError as PsycopgIntegrityError
from typing import cast


router = APIRouter(prefix="/feed-sources")


def try_commit(session: SessionDep) -> None:
    try:
        session.commit()
    except SqlAlchemyIntegrityError as exc:
        session.rollback()
        orig = cast(PsycopgIntegrityError, exc.orig)
        # PostgreSQL Error Code
        # https://www.postgresql.org/docs/current/errcodes-appendix.html
        # 23505: unique_violation
        if orig.sqlstate == "23505":
            field_name = str(orig.diag.constraint_name).removeprefix("ix_feedsource_")
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                {"field": field_name, "message": "already exists"},
            )
        else:
            raise
    except Exception:
        session.rollback()
        raise


HTTP_409_CONFLICT_RESPONSE = {
    "content": {
        "application/json": {
            "example": {"field": "feed_url", "message": "already exists"}
        }
    }
}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=FeedSourcePublic,
    responses={status.HTTP_409_CONFLICT: HTTP_409_CONFLICT_RESPONSE},
)
async def create_feed_source(feed_source: FeedSourceCreate, session: SessionDep) -> Any:
    db_feed_source = FeedSource.model_validate(feed_source)
    session.add(db_feed_source)
    try_commit(session)

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


@router.patch(
    "/{feed_source_id}",
    response_model=FeedSourcePublic,
    responses={status.HTTP_409_CONFLICT: HTTP_409_CONFLICT_RESPONSE},
)
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
    try_commit(session)
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
