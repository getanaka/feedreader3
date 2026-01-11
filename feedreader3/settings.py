import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("uvicorn." + __name__)


class Settings:
    environment: str

    scheduler_crontab_expr: str
    scheduler_misfire_grace_time: int

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int


_settings: Settings | None = None


def initialize_settings(
    load_dotenv_enabled: bool = True, dotenv_path: str | None = None
) -> None:
    global _settings
    if _settings is not None:
        logger.warning("settings has been already initialized")
        return
    _settings = Settings()

    if load_dotenv_enabled:
        load_dotenv(dotenv_path)

    _settings.environment = os.getenv("ENVIRONMENT", "dev")
    logger.info(f"settings.environment={_settings.environment}")

    _settings.scheduler_crontab_expr = os.getenv("SCHEDULER_CRONTAB_EXPR", "0 * * * *")
    logger.info(f"settings.scheduler_crontab_expr={_settings.scheduler_crontab_expr}")

    _settings.scheduler_misfire_grace_time = int(
        os.getenv("SCHEDULER_MISFIRE_GRACE_TIME", 1)
    )
    logger.info(
        f"settings.scheduler_misfire_grace_time={_settings.scheduler_misfire_grace_time}"
    )

    _settings.postgres_user = os.getenv("POSTGRES_USER", "postgres")
    logger.info(f"settings.postgres_user={_settings.postgres_user}")
    _settings.postgres_password = os.getenv("POSTGRES_PASSWORD", "password")
    _settings.postgres_db = os.getenv("POSTGRES_DB", "postgres")
    logger.info(f"settings.postgres_db={_settings.postgres_db}")
    _settings.postgres_host = os.getenv("POSTGRES_HOST", "db")
    logger.info(f"settings.postgres_host={_settings.postgres_host}")
    _settings.postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
    logger.info(f"settings.postgres_port={_settings.postgres_port}")


def finalize_settings() -> None:
    global _settings
    if _settings is None:
        logger.warning("settings is None")
        return
    _settings = None


def get_settings() -> Settings:
    if _settings is None:
        raise RuntimeError("_settings is None. Call initialize_settings()")
    return _settings
