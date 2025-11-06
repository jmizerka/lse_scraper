import asyncio

class StocksProcessor:
    def __init__(self, stocks: list[dict], crawler, semaphore_limit: int = 5):
        self.stocks = stocks
        self.semaphore = asyncio.Semaphore(semaphore_limit)
        self.crawler = crawler

    async def process_stocks(self):
        return await asyncio.gather(*[self.get_stock_data(stock) for stock in self.stocks])

    async def get_stock_data(self, stock: dict):
        async with self.semaphore:
            return self.crawler.get_stock_data(stock)
