import pandas as pd
from core.stock_processor import StocksProcessor
from core.crawler import Crawler

class CLIAdapter:

    @staticmethod
    async def run(input_csv: str, output_csv: str):
        df = pd.read_csv(input_csv).where(pd.notnull, None)
        stocks = df.to_dict(orient="records")
        async with Crawler(max_concurrent=5) as crawler:
            processor = StocksProcessor(crawler)
            results = await processor.process_stocks(stocks)
        pd.DataFrame(results).to_csv(output_csv, index=False)
