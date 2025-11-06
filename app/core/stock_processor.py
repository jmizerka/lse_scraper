import asyncio

class StocksProcessor:
    def __init__(self, crawler, semaphore_limit: int = 5):
        self.semaphore = asyncio.Semaphore(semaphore_limit)
        self.crawler = crawler

    async def process_stocks(self, stocks):
        return await asyncio.gather(*[self.get_stock_data(stock) for stock in stocks])

    async def get_stock_data(self, stock: dict):
        async with self.semaphore:
            return self.crawler.get_stock_data(stock)
