import pytest
from pytest import Session as PytestSession
from typing import Generator
from sqlmodel import Session, SQLModel, text
from sqlalchemy import Engine
from fastapi.testclient import TestClient
from feedreader3.settings import initialize_settings, get_settings
from feedreader3.database import get_engine

from feedreader3.main import app


def pytest_sessionstart(session: PytestSession) -> None:
    initialize_settings(True, "tests/.env.test")
    settings = get_settings()
    if settings.environment != "test":
        pytest.exit("Tests require environment=test")
    if not settings.postgres_db.startswith("test_"):
        pytest.exit("Tests require postgres_db=test_*")


@pytest.fixture(name="session")
def session_fixture(client: TestClient) -> Generator[Session, None, None]:
    engine = get_engine()
    truncate_all_tables(engine)
    with Session(engine) as session:
        yield session
    truncate_all_tables(engine)


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        engine = get_engine()
        truncate_all_tables(engine)
        yield client
        truncate_all_tables(engine)


def truncate_all_tables(engine: Engine) -> None:
    table_names = SQLModel.metadata.tables.keys()
    if not table_names:
        return
    with engine.begin() as conn:
        tables = ", ".join(f'"{name}"' for name in table_names)
        conn.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY CASCADE"))
