"""
Crawler
--------------
This module defines the `Crawler` class, which asynchronously retrieves
live stock data from the **London Stock Exchange (LSE)** website using Playwright.

It is designed for concurrent data fetching, supporting configurable
parallelism through an asyncio semaphore to balance performance and resource usage.

Features:
- Asynchronous crawling using `playwright.async_api`.
- Concurrency control with configurable limits.
- Automatic URL construction based on stock codes and company names.
- Extraction of price, currency, and timestamp data from company pages.
"""

import asyncio
import re
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class Crawler:

    def __init__(self, max_concurrent: int = 10):
        self.base_url = "https://www.londonstockexchange.com/stock/"
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.browser = None
        self.playwright = None
        logger.info("Crawler initialized with max_concurrent=%s", max_concurrent)

    def _build_url(self, stock: dict) -> str:
        company_name = stock["company name"].lower().replace(" ", "-")
        url = f'{self.base_url}{stock["stock code"]}/{company_name}/company-page'
        logger.debug("Built URL for %s (%s): %s", stock["company name"], stock["stock code"], url)
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
        logger.info("Fetching stock data for %s (%s)", stock["company name"], stock["stock code"])

        async with self.semaphore:
            page = await self.browser.new_page()
            try:
                await page.goto(url, timeout=30000)
                logger.debug("Navigated to %s", url)

                await page.wait_for_selector(".price-tag", timeout=30000)
                price_text = await page.text_content(".price-tag")

                await page.wait_for_selector(".bold-font-weight.refreshed-time", timeout=30000)
                timestamp = await page.text_content(".bold-font-weight.refreshed-time")

                await page.wait_for_selector(".currency-label.small-font-size.item-label strong", timeout=30000)
                currency = await page.text_content(".currency-label.small-font-size.item-label strong", timeout=30000)
                currency = re.sub(r'[^A-Za-z]', '', currency)

                logger.info("Successfully fetched data for %s", stock["company name"])

                result = {
                    "stock code": stock["stock code"],
                    "company name": stock["company name"],
                    "price": f"{price_text}{currency}",
                    "timestamp": timestamp.strip() if timestamp else None,
                    "status": "success",
                    "error": None,
                }

            except Exception as e:  # pylint:disable=broad-exception-caught
                logger.error("Error fetching data for %s (%s): %s", stock["company name"], stock["stock code"], str(e))
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
                logger.debug("Closed page for %s", stock["company name"])

        return result

    async def crawl_all(self, stocks: list[dict]) -> list[dict]:
        logger.info("Starting crawl for %s stocks...", len(stocks))
        tasks = [self.get_stock_data(stock) for stock in stocks]
        logger.info("Crawl completed for all stocks.")
        return await asyncio.gather(*tasks)
