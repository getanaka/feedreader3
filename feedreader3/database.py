from sqlmodel import SQLModel, create_engine
from sqlalchemy import Engine
from .settings import get_settings

_engine: Engine | None = None


def initialize_engine(database_file_name: str) -> None:
    # TODO: Run migration script
    global _engine
    if _engine is not None:
        raise RuntimeError("_engine is not None. _engine has already initialized")

    settings = get_settings()
    url = f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    _engine = create_engine(url)
    SQLModel.metadata.create_all(_engine)


def finalize_engine() -> None:
    global _engine
    if _engine is None:
        raise RuntimeError("_engine is None. _engine doesn't need to finalize")

    _engine.dispose()
    _engine = None


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("_engine is None. Call initialize_engine()")
    return _engine
