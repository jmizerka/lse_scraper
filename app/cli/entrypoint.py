import asyncio
import argparse
import logging
import sys
from cli.cli_adapter import CLIAdapter
from utils.logger_setup import setup_logging

setup_logging("cli")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="London Stock Exchange crawler CLI")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to input CSV file containing stock codes and company names",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Path to output CSV file to save results",
    )

    args = parser.parse_args()
    logger.info("CLI Entrypoint started")
    try:
        asyncio.run(CLIAdapter.run(args.input, args.output))
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:  # pylint:disable=broad-exception-caught
        logger.error("Fatal error: %s", str(e))
        sys.exit(1)
    finally:
        logger.info("CLI Entrypoint finished")


if __name__ == "__main__":
    main()
