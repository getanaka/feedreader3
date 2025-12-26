import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("uvicorn." + __name__)


class Settings:
    scheduler_crontab_expr: str
    scheduler_misfire_grace_time: int

    database_file_name: str


_settings: Settings = Settings()


def initialize_settings(
    load_dotenv_enabled: bool = True, dotenv_path: str | None = None
) -> None:
    if load_dotenv_enabled:
        load_dotenv(dotenv_path)

    _settings.scheduler_crontab_expr = os.getenv("SCHEDULER_CRONTAB_EXPR", "0 * * * *")
    logger.info(f"settings.scheduler_crontab_expr={_settings.scheduler_crontab_expr}")

    _settings.scheduler_misfire_grace_time = int(
        os.getenv("SCHEDULER_MISFIRE_GRACE_TIME", 1)
    )
    logger.info(
        f"settings.scheduler_misfire_grace_time={_settings.scheduler_misfire_grace_time}"
    )

    _settings.database_file_name = os.getenv("DATABASE_FILE_NAME", "database.db")
    logger.info(f"settings.database_file_name={_settings.database_file_name}")


def get_settings() -> Settings:
    return _settings
