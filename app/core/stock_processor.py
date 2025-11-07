import logging


logger = logging.getLogger(__name__)


class StocksProcessor:
    def __init__(self, crawler):
        self.crawler = crawler

    async def process_stocks(self, stocks: list[dict]) -> list[dict]:
        logger.info(f"Starting stock processing for {len(stocks)} entries...")
        try:
            results = await self.crawler.crawl_all(stocks)
        except Exception as e:
            logger.exception(f"Unexpected error during crawling: {e}")
            return []
        succeeded = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") != "success"]
        logger.info(f"Processing complete. Success: {len(succeeded)}, Failed: {len(failed)}")
        if failed:
            for item in failed:
                # you could easily plug in some notification system here
                logger.warning(
                    f"Failed: {item['company name']} ({item['stock code']}) | Error: {item['error']}"
                )
        return succeeded
