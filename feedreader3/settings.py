import os
from dotenv import load_dotenv


class Settings:
    scheduler_crontab_expr: str
    scheduler_misfire_grace_time: int


_settings: Settings = Settings()


def initialize_settings(
    load_dotenv_enabled: bool = True, dotenv_path: str | None = None
) -> None:
    if load_dotenv_enabled:
        load_dotenv(dotenv_path)

    _settings.scheduler_crontab_expr = os.getenv("SCHEDULER_CRONTAB_EXPR", "0 * * * *")
    _settings.scheduler_misfire_grace_time = int(
        os.getenv("SCHEDULER_MISFIRE_GRACE_TIME", 1)
    )


def get_settings() -> Settings:
    return _settings
