import asyncio
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self, max_concurrent: int = 10):
        self.base_url = "https://www.londonstockexchange.com/stock/"
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.browser = None
        self.playwright = None
        logger.info(f"Crawler initialized with max_concurrent={max_concurrent}")

    def _build_url(self, stock: dict) -> str:
        company_name = stock["company name"].lower().replace(" ", "-")
        url = f'{self.base_url}{stock["stock code"]}/{company_name}/company-page'
        logger.debug(f"Built URL for {stock['company name']} ({stock['stock code']}): {url}")
        return url


    async def __aenter__(self):
        logger.info("Starting Playwright and launching browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Browser launched successfully.")
        return self

    async def __aexit__(self, *args):
        logger.info("Closing browser and stopping Playwright...")
        await self.browser.close()
        await self.playwright.stop()
        logger.info("Browser and Playwright shut down cleanly.")


    async def get_stock_data(self, stock: dict) -> dict:
        url = self._build_url(stock)
        logger.info(f"Fetching stock data for {stock['company name']} ({stock['stock code']})")

        async with self.semaphore:
            page = await self.browser.new_page()
            try:
                await page.goto(url, timeout=30000)
                logger.debug(f"Navigated to {url}")

                await page.wait_for_selector(".price-tag", timeout=10000)
                price_text = await page.text_content(".price-tag")

                await page.wait_for_selector(".bold-font-weight.refreshed-time", timeout=10000)
                timestamp = await page.text_content(".bold-font-weight.refreshed-time")

                logger.info(f"Successfully fetched data for {stock['company name']}")

                result = {
                    "stock code": stock["stock code"],
                    "company name": stock["company name"],
                    "price": price_text,
                    "timestamp": timestamp.strip() if timestamp else None,
                    "status": "success",
                    "error": None,
                }

            except Exception as e:
                logger.error(f"Error fetching data for {stock['company name']} ({stock['stock code']}): {e}")
                result = {
                    "stock code": stock["stock code"],
                    "company name": stock["company name"],
                    "price": None,
                    "timestamp": None,
                    "status": "failed",
                    "error": str(e),
                }

            finally:
                await page.close()
                logger.debug(f"Closed page for {stock['company name']}")

        return result

    async def crawl_all(self, stocks: list[dict]) -> list[dict]:
        logger.info(f"Starting crawl for {len(stocks)} stocks...")
        tasks = [self.get_stock_data(stock) for stock in stocks]
        logger.info("Crawl completed for all stocks.")
        return await asyncio.gather(*tasks)
