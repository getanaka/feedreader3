import os

from feedreader3.settings import initialize_settings, get_settings

SCHEDULER_CRONTAB_EXPR = "SCHEDULER_CRONTAB_EXPR"
SCHEDULER_MISFIRE_GRACE_TIME = "SCHEDULER_MISFIRE_GRACE_TIME"
DATABASE_FILE_NAME = "DATABASE_FILE_NAME"


def test_settings() -> None:
    crontab_expr = "*/10 * * * *"
    misfire_grace_time = 30
    database_file_name = "test_database.db"

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)
    os.environ.pop(DATABASE_FILE_NAME, None)

    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)
    os.environ.pop(DATABASE_FILE_NAME, None)

    assert settings.scheduler_crontab_expr == crontab_expr
    assert settings.scheduler_misfire_grace_time == misfire_grace_time
    assert settings.database_file_name == database_file_name


def test_settings_load_from_os() -> None:
    crontab_expr = "*/1 * * * *"

    os.environ[SCHEDULER_CRONTAB_EXPR] = crontab_expr

    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)

    assert settings.scheduler_crontab_expr == crontab_expr


def test_settings_load_from_dotenv() -> None:
    crontab_expr = "*/10 * * * *"

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)

    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)

    assert settings.scheduler_crontab_expr == crontab_expr


def test_settings_load_default() -> None:
    # defaults from settings.py
    crontab_expr = "0 * * * *"

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)

    initialize_settings(False)
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)

    assert settings.scheduler_crontab_expr == crontab_expr
