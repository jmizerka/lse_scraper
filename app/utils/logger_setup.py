"""
Logger Setup
------------------
This module provides a utility function `setup_logging` to configure structured logging
for the application. It supports logging to both the console and rotating log files
with configurable log levels.

Features:
- Logs are written to a `logs/` directory (or directory specified by LOG_DIR environment variable).
- Timed rotating log files (daily rotation at midnight) with retention of 90 days.
- Console logging to stdout.
- Log level configurable via LOG_LEVEL environment variable (default: INFO).
- Log messages formatted with timestamp, logger name, level, and message.

"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


def setup_logging(file_name):
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{file_name}.log")
    log_level_str = os.getenv("LOG_LEVEL", "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, delay=True, backupCount=90, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    file_handler.suffix = "%Y-%m-%d.log"
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    logging.basicConfig(level=log_level, handlers=[file_handler, stream_handler])
