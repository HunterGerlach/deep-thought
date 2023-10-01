"""Module to set up a colored logger."""

import logging
from termcolor import colored

from config import Config

config = Config()
log_level = config.get("LOG_LEVEL", "INFO")

class ColoredFormatter(logging.Formatter):
    """Formatter class to color log levels."""

    COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }

    def format(self, record):
        local_log_level = record.levelname
        log_message = super().format(record)
        colored_level = colored(local_log_level, self.COLORS.get(local_log_level))
        return log_message.replace(local_log_level, colored_level)

def setup_logger():
    """Set up and return a logger with colored log levels."""

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(levelname)s: %(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

    formatter = ColoredFormatter("%(levelname)s: %(asctime)s - %(message)s")

    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    return logging.getLogger()
