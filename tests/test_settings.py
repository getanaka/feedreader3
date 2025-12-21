import os

from feedreader3.settings import initialize_settings, get_settings

SCHEDULER_CRONTAB_EXPR = "SCHEDULER_CRONTAB_EXPR"
SCHEDULER_MISFIRE_GRACE_TIME = "SCHEDULER_MISFIRE_GRACE_TIME"


def test_settings_load_from_os() -> None:
    crontab_expr = "*/1 * * * *"
    misfire_grace_time = 42

    os.environ[SCHEDULER_CRONTAB_EXPR] = crontab_expr
    os.environ[SCHEDULER_MISFIRE_GRACE_TIME] = str(misfire_grace_time)

    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)

    assert settings.scheduler_crontab_expr == crontab_expr
    assert settings.scheduler_misfire_grace_time == misfire_grace_time


def test_settings_load_from_dotenv() -> None:
    crontab_expr = "*/10 * * * *"
    misfire_grace_time = 30

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)

    initialize_settings(True, "tests/.env.test")
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)

    assert settings.scheduler_crontab_expr == crontab_expr
    assert settings.scheduler_misfire_grace_time == misfire_grace_time


def test_settings_load_default() -> None:
    # defaults from settings.py
    crontab_expr = "0 * * * *"
    misfire_grace_time = 1

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)

    initialize_settings(False)
    settings = get_settings()

    os.environ.pop(SCHEDULER_CRONTAB_EXPR, None)
    os.environ.pop(SCHEDULER_MISFIRE_GRACE_TIME, None)

    assert settings.scheduler_crontab_expr == crontab_expr
    assert settings.scheduler_misfire_grace_time == misfire_grace_time
