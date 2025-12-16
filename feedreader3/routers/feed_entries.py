from typing import Annotated, Sequence, Literal, cast
from fastapi import Query, APIRouter
from sqlmodel import select, func, Column
from datetime import datetime
from ..dependencies import SessionDep
from ..models.feed_entry import FeedEntry

router = APIRouter(prefix="/feed-entries")


@router.get("")
async def read_feed_entries(
    session: SessionDep,
    start: datetime = datetime.min,
    end: datetime = datetime.max,
    order: Literal["asc", "desc"] = "asc",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Sequence[FeedEntry]:
    ts = func.coalesce(FeedEntry.entry_updated_at, FeedEntry.first_seen_at)
    ts_order = ts.asc() if order == "asc" else ts.desc()
    id_col = cast(Column[int], FeedEntry.id)
    id_order = id_col.asc() if order == "asc" else id_col.desc()
    feed_entries = session.exec(
        select(FeedEntry)
        .where(start <= ts, ts <= end)
        .order_by(ts_order, id_order)
        .offset(offset)
        .limit(limit)
    ).all()
    return feed_entries
