import sys
from loguru import logger as _logger
from config.settings import settings


def setup_logger():
    """Configure loguru with console and file handlers."""
    _logger.remove()

    _logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _logger.add(
        settings.LOGS_DIR / "ewu_scraper_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    return _logger


logger = setup_logger()
