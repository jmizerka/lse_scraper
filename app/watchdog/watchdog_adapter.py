import os
import logging
from datetime import datetime
from watchfiles import awatch, Change
from core.crawler import Crawler
from core.stocks_processor import StocksProcessor
from core.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class WatcherAdapter:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        logger.info(f"WatcherAdapter initialized. Watching: '{input_dir}', Output: '{output_dir}'")

    async def watch(self):
        logger.info(f"Started watching directory: {self.input_dir}")
        try:
            async for changes in awatch(self.input_dir):
                for change, path in changes:
                    if change == Change.added and path.endswith(".csv"):
                        logger.info(f"Detected new CSV file: {path}")
                        await self._process_file(path)
        except Exception as e:
            logger.error(f"Error while watching directory '{self.input_dir}': {e}")
            raise
        finally:
            logger.info(f"Stopped watching directory: {self.input_dir}")

    async def _process_file(self, file_path: str):
        logger.info(f"Processing file: {file_path}")
        try:
            stocks = CSVHandler.read_csv(file_path)
            logger.info(f"Loaded {len(stocks)} stock entries from {file_path}")
            async with Crawler(max_concurrent=5) as crawler:
                processor = StocksProcessor(crawler)
                logger.info("Processing stock data...")
                results = await processor.process_stocks(stocks)
                logger.info(f"Completed processing for {file_path}")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"stocks_output_{timestamp}.csv"
            output_path = os.path.join(self.output_dir, output_filename)
            CSVHandler.write_csv(results, output_path)
            logger.info(f"Results saved to {output_path}")
        except Exception as e:
            logger.exception(f"Error processing file '{file_path}': {e}")
            raise