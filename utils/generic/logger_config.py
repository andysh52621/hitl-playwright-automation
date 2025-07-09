import logging
from logging.handlers import TimedRotatingFileHandler


def configure_logging():
    """
    Configures logging specifically for the HitlLogger.
    Logs to both console and rotating file. Suppresses other loggers.
    """
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # File handler: rotates daily, keeps 7 days
    file_handler = TimedRotatingFileHandler("Hitl_test.log", when="midnight", backupCount=7, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Set up Playwright-specific logger
    playwright_logger = logging.getLogger("HitlLogger")
    playwright_logger.setLevel(logging.INFO)
    playwright_logger.handlers.clear()
    playwright_logger.addHandler(console_handler)
    playwright_logger.addHandler(file_handler)
    playwright_logger.propagate = False  # Avoid double logging

    # Suppress root logger and other noisy libraries
# logging.getLogger().handlers.clear()
# logging.getLogger().setLevel(logging.WARNING)
