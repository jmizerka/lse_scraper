import asyncio
import pandas as pd
from core.stock_processor import StockProcessor

class CLIAdapter:

    def __init__(self, stock_processor: StockProcessor):
        self.stock_processor = stock_processor

    def run(self, input_csv: str, output_csv: str):
        df = pd.read_csv(input_csv)
        stocks = df.to_dict(orient="records")
        results = asyncio.run(self.stock_processor.process_stocks(stocks))
        pd.DataFrame(results).to_csv(output_csv, index=False)
