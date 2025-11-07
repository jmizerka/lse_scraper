class StocksProcessor:
    def __init__(self, crawler):
        self.crawler = crawler

    async def process_stocks(self, stocks: list[dict]) -> list[dict]:
        return await self.crawler.crawl_all(stocks)