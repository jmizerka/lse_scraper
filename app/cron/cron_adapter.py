import asyncio
import logging
from pathlib import Path
import pandas as pd
from aiocron import crontab

from core.crawler import Crawler
from core.stocks_processor import StocksProcessor
from core.csv_handler import CSVHandler

logger = logging.getLogger(__name__)


class CronAdapter:
    def __init__(self, input_csv: str, output_csv: str, cron_expr: str = "*/5 * * * *"):
        self.input_csv = Path(input_csv)
        self.output_csv = Path(output_csv)
        self.cron_expr = cron_expr
        logger.info(f"CronAdapter initialized: input={input_csv}, output={output_csv}, schedule={cron_expr}")

    async def _process_file(self):
        logger.info("Cron job started...")
        try:
            stocks = CSVHandler.read_csv(self.input_csv)
            logger.info(f"Loaded {len(stocks)} stock entries from {self.input_csv}")
            async with Crawler(max_concurrent=5) as crawler:
                processor = StocksProcessor(crawler)
                logger.info("Starting async stock processing...")
                results = await processor.process_stocks(stocks)
            CSVHandler.write_csv(results, self.output_csv, append=True)
            logger.info(f"Cron job results appended to {self.output_csv}")
        except Exception as e:
            logger.exception(f"Error during cron job execution': {e}")

    async def _cron_task(self):
        await self._process_file()

    async def start(self):
        logger.info(f"Starting CronAdapter schedule: {self.cron_expr}")
        job = crontab(self.cron_expr, func=self._cron_task)
        await asyncio.Event().wait()
