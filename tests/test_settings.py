import os
import pytest
from typing import Generator, Any

from feedreader3.settings import initialize_settings, finalize_settings, get_settings


ENVIRONMENT = "ENVIRONMENT"
SCHEDULER_CRONTAB_EXPR = "SCHEDULER_CRONTAB_EXPR"
SCHEDULER_MISFIRE_GRACE_TIME = "SCHEDULER_MISFIRE_GRACE_TIME"
POSTGRES_USER = "POSTGRES_USER"
POSTGRES_PASSWORD = "POSTGRES_PASSWORD"
POSTGRES_DB = "POSTGRES_DB"
POSTGRES_HOST = "POSTGRES_HOST"
POSTGRES_PORT = "POSTGRES_PORT"


def pop_environ(key: str) -> str | None:
    return os.environ.pop(key, None)


def push_environ(key: str, value: str | None) -> None:
    if value is None:
        return
    os.environ[key] = value


@pytest.fixture(name="reset_settings")
def settings_fixture() -> Generator[Any, Any, Any]:
    # Revert to unitinialized
    finalize_settings()
    environment = pop_environ(ENVIRONMENT)
    scheduler_crontab_expr = pop_environ(SCHEDULER_CRONTAB_EXPR)
    scheduler_misfire_grace_time = pop_environ(SCHEDULER_MISFIRE_GRACE_TIME)
    postgres_user = pop_environ(POSTGRES_USER)
    postgres_password = pop_environ(POSTGRES_PASSWORD)
    postgres_db = pop_environ(POSTGRES_DB)
    postgres_host = pop_environ(POSTGRES_HOST)
    postgres_port = pop_environ(POSTGRES_PORT)

    yield

    finalize_settings()
    push_environ(ENVIRONMENT, environment)
    push_environ(SCHEDULER_CRONTAB_EXPR, scheduler_crontab_expr)
    push_environ(SCHEDULER_MISFIRE_GRACE_TIME, scheduler_misfire_grace_time)
    push_environ(POSTGRES_USER, postgres_user)
    push_environ(POSTGRES_PASSWORD, postgres_password)
    push_environ(POSTGRES_DB, postgres_db)
    push_environ(POSTGRES_HOST, postgres_host)
    push_environ(POSTGRES_PORT, postgres_port)

    initialize_settings()


def test_initialize_settings_valid_environment_variables(reset_settings: Any) -> None:
    environment = "dev"
    scheduler_crontab_expr = "* * * * *"
    scheduler_misfire_grace_time = "100"
    postgres_user = "user"
    postgres_password = "password"
    postgres_db = "db"
    postgres_host = "host"
    postgres_port = "100"

    os.environ[ENVIRONMENT] = environment
    os.environ[SCHEDULER_CRONTAB_EXPR] = scheduler_crontab_expr
    os.environ[SCHEDULER_MISFIRE_GRACE_TIME] = scheduler_misfire_grace_time
    os.environ[POSTGRES_USER] = postgres_user
    os.environ[POSTGRES_PASSWORD] = postgres_password
    os.environ[POSTGRES_DB] = postgres_db
    os.environ[POSTGRES_HOST] = postgres_host
    os.environ[POSTGRES_PORT] = postgres_port

    initialize_settings()
    settings = get_settings()

    assert settings.environment == environment
    assert settings.scheduler_crontab_expr == scheduler_crontab_expr
    assert settings.scheduler_misfire_grace_time == int(scheduler_misfire_grace_time)
    assert settings.postgres_user == postgres_user
    assert settings.postgres_password == postgres_password
    assert settings.postgres_db == postgres_db
    assert settings.postgres_host == postgres_host
    assert settings.postgres_port == int(postgres_port)


def test_initialize_settings_invalid_environment_variables(reset_settings: Any) -> None:
    with pytest.raises(ValueError) as excinfo:
        initialize_settings()

    assert str(excinfo.value) == "POSTGRES_USER is None"
