# adapters/watcher_adapter.py
import asyncio
import os
import pandas as pd
from datetime import datetime
from watchfiles import awatch, Change

from core.stocks_processor import StocksProcessor


class WatcherAdapter:
    def __init__(self, input_dir: str, output_dir: str, stocks_processor: StocksProcessor):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.stocks_processor = stocks_processor

    async def watch(self):
        async for changes in awatch(self.input_dir):
            for change, path in changes:
                if change == Change.added and path.endswith(".csv"):
                    await self._process_file(path)

    async def _process_file(self, file_path: str):
        df = pd.read_csv(file_path).where(pd.notnull, None)
        stocks = df.to_dict(orient="records")
        results = await self.stocks_processor.process_stocks(stocks)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"stocks_output_{timestamp}.csv"
        output_path = os.path.join(self.output_dir, output_filename)
        pd.DataFrame(results).to_csv(output_path, index=False)