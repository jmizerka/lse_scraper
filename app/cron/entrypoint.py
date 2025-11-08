import asyncio
import argparse
import logging
import signal
from pathlib import Path
import sys
from cron.cron_adapter import CronAdapter
from utils.logger_setup import setup_logging


setup_logging("cron")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Run CronAdapter for periodic stock updates.")
    parser.add_argument("--input", required=True, help="Path to the input CSV file containing stock symbols and names.")
    parser.add_argument("--output", required=True, help="Path where the output CSV with stock results will be saved.")
    parser.add_argument(
        "--cron", default="*/5 * * * *", help="Cron expression defining the schedule (default: every 5 minutes)."
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        logging.error("Input file not found: %s", input_path)
        sys.exit(1)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    adapter = CronAdapter(
        input_csv=str(input_path),
        output_csv=str(output_path),
        cron_expr=args.cron,
    )
    stop_event = asyncio.Event()

    def _signal_handler():
        logging.info("Shutdown signal received. Stopping CronAdapter gracefully...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:  # signals won't work on Windows
            logging.warning("Signal handling not fully supported on this platform.")

    logging.info("CronAdapter service starting...")
    cron_task = asyncio.create_task(adapter.start())
    await stop_event.wait()
    logging.info("Shutting down CronAdapter...")
    cron_task.cancel()
    try:
        await cron_task
    except asyncio.CancelledError:
        logging.info("CronAdapter stopped cleanly.")
    logging.info("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Interrupted by user. Exiting...")
