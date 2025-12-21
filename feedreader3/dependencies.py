from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session
from .database import get_engine


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
