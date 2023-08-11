import logging
from termcolor import colored

from src.config import LOG_LEVEL

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
    }

    def format(self, record):
        log_level = record.levelname
        log_message = super().format(record)
        return log_message.replace(log_level, colored(log_level, self.COLORS.get(log_level)))

def setup_logger():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
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
