from typing import Annotated, Sequence, Literal, cast
from fastapi import Query, APIRouter
from sqlmodel import select, func, Column
from datetime import datetime
from ..dependencies import SessionDep
from ..models.feed_entry import FeedEntry
from pydantic import AfterValidator

router = APIRouter(prefix="/feed-entries")


def check_timezone_aware_datetime(dt: datetime) -> datetime:
    # https://docs.python.org/3.14/library/datetime.html#determining-if-an-object-is-aware-or-naive
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        return dt
    raise ValueError("Invalid datetime, it must be timezone-aware")


@router.get("")
async def read_feed_entries(
    session: SessionDep,
    start: Annotated[
        datetime | None, AfterValidator(check_timezone_aware_datetime)
    ] = None,
    end: Annotated[
        datetime | None, AfterValidator(check_timezone_aware_datetime)
    ] = None,
    order: Literal["asc", "desc"] = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[FeedEntry]:
    ts = func.coalesce(FeedEntry.entry_updated_at, FeedEntry.first_seen_at)
    ts_order = ts.asc() if order == "asc" else ts.desc()
    id_col = cast(Column[int], FeedEntry.id)
    id_order = id_col.asc() if order == "asc" else id_col.desc()

    query = select(FeedEntry)
    if start is not None:
        query = query.where(start <= ts)
    if end is not None:
        query = query.where(ts <= end)
    query = query.order_by(ts_order, id_order).offset(offset).limit(limit)

    feed_entries = session.exec(query).all()
    return feed_entries
