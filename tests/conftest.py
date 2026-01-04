import pytest
from pytest import Session as PytestSession, ExitCode
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from feedreader3.settings import initialize_settings, get_settings
from sqlalchemy import text

from feedreader3.dependencies import get_session
from feedreader3.main import app

TEST_POSTGRES_USER: str = "test_postgres"
TEST_POSTGRES_PASSWORD: str = "test_password"
TEST_POSTGRES_DB: str = "test_postgres"


def pytest_sessionstart(session: PytestSession) -> None:
    initialize_settings()

    # create test database
    settings = get_settings()
    engine = create_engine(
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/template1",
        isolation_level="AUTOCOMMIT",
    )
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_POSTGRES_DB} WITH (FORCE)"))
        conn.execute(text(f"DROP USER IF EXISTS {TEST_POSTGRES_USER}"))
        conn.execute(
            text(
                f"CREATE USER {TEST_POSTGRES_USER} WITH PASSWORD '{TEST_POSTGRES_PASSWORD}'"
            )
        )
        conn.execute(
            text(f"CREATE DATABASE {TEST_POSTGRES_DB} OWNER {TEST_POSTGRES_USER}")
        )


def pytest_sessionfinish(session: PytestSession, exitstatus: int | ExitCode) -> None:
    # drop test database
    settings = get_settings()
    engine = create_engine(
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/template1",
        isolation_level="AUTOCOMMIT",
    )
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_POSTGRES_DB} WITH (FORCE)"))
        conn.execute(text(f"DROP USER IF EXISTS {TEST_POSTGRES_USER}"))


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        f"postgresql+psycopg://{TEST_POSTGRES_USER}:{TEST_POSTGRES_PASSWORD}@localhost:5432/{TEST_POSTGRES_DB}"
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    client.close()
    app.dependency_overrides.clear()
