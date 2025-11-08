import logging
from app.core.stock_processor import StocksProcessor
from app.core.crawler import Crawler
from app.core.csv_handler import CSVHandler

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
