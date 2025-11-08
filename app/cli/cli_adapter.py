import logging
from core.stock_processor import StocksProcessor
from core.crawler import Crawler
from core.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class CLIAdapter:

    @staticmethod
    async def run(input_csv: str, output_csv: str):
        logger.info(f"Starting CLIAdapter run with input='{input_csv}' and output='{output_csv}'")
        try:
            logger.info(f"Reading input CSV: {input_csv}")
            stocks = CSVHandler.read_csv(input_csv)
            logger.info(f"Loaded {len(stocks)} stock entries from CSV")
            async with Crawler(max_concurrent=5) as crawler:
                processor = StocksProcessor(crawler)
                logger.info("Processing stocks asynchronously...")
                results = await processor.process_stocks(stocks)
                logger.info("Stock processing completed successfully.")
            logger.info(f"Saving results to {output_csv}")
            CSVHandler.write_csv(data = results, path = output_csv, append=True)
            logger.info("Output CSV written successfully.")
        except Exception as e:
            logger.exception(f"Error during CLIAdapter run: {e}")
            raise
        logger.info("CLIAdapter run completed.")