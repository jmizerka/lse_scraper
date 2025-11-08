"""
Watchdog CLI Entrypoint
------------------------------
This module provides a command-line interface (CLI) to monitor a directory
for new CSV files and automatically process them using the `WatcherAdapter`.

Features:
- Watches a specified input directory for new CSV files.
- Automatically processes detected CSV files and saves output to a target directory.
- Uses asynchronous execution for efficient file monitoring and processing.
"""

import asyncio
import argparse
import logging
import sys
from watchdog.watchdog_adapter import WatcherAdapter
from utils.logger_setup import setup_logging


setup_logging("watchdog")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Watch a directory for new CSV files and automatically process them.")

    parser.add_argument("--input-dir", "-i", required=True, help="Directory to watch for new CSV files.")
    parser.add_argument("--output-dir", "-o", required=True, help="Directory to save processed CSV output.")

    args = parser.parse_args()
    logger.info("Watcher Entrypoint started")

    try:
        adapter = WatcherAdapter(args.input_dir, args.output_dir)
        asyncio.run(adapter.watch())
    except KeyboardInterrupt:
        logger.warning("Watcher stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:  # pylint:disable=broad-exception-caught
        logger.exception("Fatal error in Watcher: %s", str(e))
        sys.exit(1)
    finally:
        logger.info("Watcher Entrypoint finished")


if __name__ == "__main__":
    main()
