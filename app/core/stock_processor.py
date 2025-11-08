import logging


logger = logging.getLogger(__name__)


class StocksProcessor:
    def __init__(self, crawler):
        self.crawler = crawler

    async def process_stocks(self, stocks: list[dict]) -> list[dict]:
        logger.info("Starting stock processing for %s entries...", len(stocks))
        try:
            results = await self.crawler.crawl_all(stocks)
        except Exception as e:  # pylint:disable=broad-exception-caught
            logger.exception("Unexpected error during crawling: %s", str(e))
            return []
        succeeded = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") != "success"]
        logger.info("Processing complete. Success: %s, Failed: %s", len(succeeded), len(failed))
        if failed:
            for item in failed:
                # you could easily plug in some notification system here
                logger.warning("Failed: %s (%s) | Error: %s", item["company name"], item["stock code"], item["error"])
        return succeeded
