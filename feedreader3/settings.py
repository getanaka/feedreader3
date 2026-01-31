import os
import logging

logger = logging.getLogger("uvicorn." + __name__)


class Settings:
    scheduler_crontab_expr: str
    scheduler_misfire_grace_time: int

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int


_settings: Settings | None = None


def initialize_settings() -> None:
    global _settings
    if _settings is not None:
        logger.warning("settings has been already initialized")
        return

    settings = Settings()

    settings.scheduler_crontab_expr = os.getenv(
        "SCHEDULER_CRONTAB_EXPR", "*/10 * * * *"
    )
    logger.info(f"settings.scheduler_crontab_expr={settings.scheduler_crontab_expr}")

    settings.scheduler_misfire_grace_time = int(
        os.getenv("SCHEDULER_MISFIRE_GRACE_TIME", 30)
    )
    logger.info(
        f"settings.scheduler_misfire_grace_time={settings.scheduler_misfire_grace_time}"
    )

    settings.postgres_user = get_required_environment_variable("POSTGRES_USER")
    logger.info(f"settings.postgres_user={settings.postgres_user}")

    settings.postgres_password = get_required_environment_variable("POSTGRES_PASSWORD")

    settings.postgres_db = get_required_environment_variable("POSTGRES_DB")
    logger.info(f"settings.postgres_db={settings.postgres_db}")

    settings.postgres_host = get_required_environment_variable("POSTGRES_HOST")
    logger.info(f"settings.postgres_host={settings.postgres_host}")

    settings.postgres_port = int(get_required_environment_variable("POSTGRES_PORT"))
    logger.info(f"settings.postgres_port={settings.postgres_port}")

    _settings = settings


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


def get_required_environment_variable(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"{key} is None")
    return value
