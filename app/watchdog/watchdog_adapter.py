import os
import asyncio
import logging
from datetime import datetime
from watchfiles import awatch, Change
from core.crawler import Crawler
from core.stock_processor import StocksProcessor
from core.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class WatcherAdapter:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        os.makedirs(self.input_dir, exist_ok=True)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("WatcherAdapter initialized. Watching: '%s', Output: '%s'", input_dir, output_dir)

    async def watch(self):
        await asyncio.sleep(1)
        logger.info("Started watching directory: %s", self.input_dir)
        try:
            async for changes in awatch(self.input_dir):
                for change, path in changes:
                    if change == Change.added and path.endswith(".csv"):
                        logger.info("Detected new CSV file: %s", path)
                        await self._process_file(path)
        except Exception as e:
            logger.error("Error while watching directory '%s': %s", self.input_dir, str(e))
            raise
        finally:
            logger.info("Stopped watching directory: %s", self.input_dir)

    async def _process_file(self, file_path: str):
        logger.info("Processing file: %s", file_path)
        try:
            stocks = CSVHandler.read_csv(file_path)
            logger.info("Loaded %s stock entries from %s", len(stocks), file_path)
            async with Crawler(max_concurrent=5) as crawler:
                processor = StocksProcessor(crawler)
                logger.info("Processing stock data...")
                results = await processor.process_stocks(stocks)
                logger.info("Completed processing for %s", file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"stocks_output_{timestamp}.csv"
            output_path = os.path.join(self.output_dir, output_filename)
            CSVHandler.write_csv(results, output_path)
            logger.info("Results saved to %s", output_path)
        except Exception as e:
            logger.exception("Error processing file '%s': %s", file_path, str(e))
            raise
