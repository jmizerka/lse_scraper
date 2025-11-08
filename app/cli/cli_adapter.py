"""
CLI Adapter Module
------------------
This module defines the `CLIAdapter` class, which provides a command-line interface
for processing stock data using the same underlying logic as the API.

The adapter reads stock data from an input CSV file, processes each stock asynchronously
(using the `Crawler` and `StocksProcessor`), and writes the processed results to an output CSV.

It is designed to be invoked by a CLI entry point.
"""

import logging
from core.stock_processor import StocksProcessor
from core.crawler import Crawler
from core.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class CLIAdapter:

    @staticmethod
    async def run(input_csv: str, output_csv: str):
        logger.info("Starting CLIAdapter run with input='%s' and output='%s'", input_csv, output_csv)
        try:
            logger.info("Reading input CSV: %s", input_csv)
            stocks = CSVHandler.read_csv(input_csv)
            logger.info("Loaded %s stock entries from CSV", len(stocks))
            async with Crawler(max_concurrent=5) as crawler:
                processor = StocksProcessor(crawler)
                logger.info("Processing stocks asynchronously...")
                results = await processor.process_stocks(stocks)
                logger.info("Stock processing completed successfully.")
            logger.info("Saving results to %s", output_csv)
            CSVHandler.write_csv(data=results, path=output_csv, append=True)
            logger.info("Output CSV written successfully.")
        except Exception as e:
            logger.exception("Error during CLIAdapter run: %s", str(e))
            raise
        logger.info("CLIAdapter run completed.")
