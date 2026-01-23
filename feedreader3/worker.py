from .database import initialize_engine, finalize_engine
from .scheduler import (
    initialize_scheduler,
    startup_scheduler,
)
from .settings import initialize_settings, get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("worker started")
    # settings
    initialize_settings()
    settings = get_settings()

    # DB
    initialize_engine()

    # scheduler
    initialize_scheduler(
        settings.scheduler_crontab_expr, settings.scheduler_misfire_grace_time
    )

    try:
        startup_scheduler()
    except (KeyboardInterrupt, SystemExit) as exc:
        logger.info(f"worker stopped: {type(exc).__name__}")
    finally:
        finalize_engine()


if __name__ == "__main__":
    main()
