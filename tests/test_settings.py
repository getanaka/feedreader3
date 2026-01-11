import os
import pytest
from typing import Generator, Any

from feedreader3.settings import initialize_settings, finalize_settings, get_settings

SCHEDULER_CRONTAB_EXPR = "SCHEDULER_CRONTAB_EXPR"
SCHEDULER_MISFIRE_GRACE_TIME = "SCHEDULER_MISFIRE_GRACE_TIME"
POSTGRES_USER = "POSTGRES_USER"
POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
POSTGRES_DB = "POSTGRES_DB"
POSTGRES_HOST = "POSTGRES_HOST"
POSTGRES_PORT = "POSTGRES_PORT"


@pytest.fixture(name="reset_settings")
def settings_fixture() -> Generator[Any, Any, Any]:
    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)
    os.environ.pop(POSTGRES_USER, None)
    os.environ.pop(POSTGRES_PASSWORD, None)
    os.environ.pop(POSTGRES_DB, None)
    os.environ.pop(POSTGRES_HOST, None)
    os.environ.pop(POSTGRES_PORT, None)

    yield

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)
    os.environ.pop(POSTGRES_USER, None)
    os.environ.pop(POSTGRES_PASSWORD, None)
    os.environ.pop(POSTGRES_DB, None)
    os.environ.pop(POSTGRES_HOST, None)
    os.environ.pop(POSTGRES_PORT, None)
    finalize_settings()
    initialize_settings(True, "tests/.env.test")


def test_settings(reset_settings: Any) -> None:
    crontab_expr = "*/10 * * * *"
    misfire_grace_time = 30
    postgres_user = "test_postgres"
    postgres_password = "test_password"
    postgres_db = "test_postgres"
    postgres_host = "localhost"
    postgres_port = 5432

    finalize_settings()
    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    assert settings.scheduler_crontab_expr == crontab_expr
    assert settings.scheduler_misfire_grace_time == misfire_grace_time
    assert settings.postgres_user == postgres_user
    assert settings.postgres_password == postgres_password
    assert settings.postgres_db == postgres_db
    assert settings.postgres_host == postgres_host
    assert settings.postgres_port == postgres_port


def test_settings_load_from_os(reset_settings: Any) -> None:
    crontab_expr = "*/1 * * * *"

    os.environ[SCHEDULER_CRONTAB_EXPR] = crontab_expr

    finalize_settings()
    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    assert settings.scheduler_crontab_expr == crontab_expr


def test_settings_load_from_dotenv(reset_settings: Any) -> None:
    crontab_expr = "*/10 * * * *"

    finalize_settings()
    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    assert settings.scheduler_crontab_expr == crontab_expr


def test_settings_load_default(reset_settings: Any) -> None:
    # defaults from settings.py
    crontab_expr = "0 * * * *"

    finalize_settings()
    initialize_settings(False)
    settings = get_settings()

    assert settings.scheduler_crontab_expr == crontab_expr
