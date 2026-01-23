import logging
import logging.config
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/app.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            )
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": LOG_LEVEL,
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": LOG_FILE,
            "level": LOG_LEVEL,
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
}


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
