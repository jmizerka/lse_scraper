import asyncio
import re
from playwright.async_api import async_playwright


class Crawler:

    def __init__(self, max_concurrent: int = 10):
        self.base_url = "https://www.londonstockexchange.com/stock/"
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.browser = None
        self.playwright = None

    def _build_url(self, stock: dict) -> str:
        company_name = stock["company name"].lower().replace(" ", "-")
        return f'{self.base_url}{stock["stock code"]}/{company_name}/company-page'

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(self, *args):
        await self.browser.close()
        await self.playwright.stop()

    async def get_stock_data(self, stock: dict) -> dict:
        url = self._build_url(stock)

        async with self.semaphore:
            page = await self.browser.new_page()
            try:
                await page.goto(url, timeout=30000)

                await page.wait_for_selector(".price-tag", timeout=10000)
                price_text = await page.text_content(".price-tag")

                await page.wait_for_selector(".bold-font-weight.refreshed-time", timeout=10000)
                timestamp = await page.text_content(".bold-font-weight.refreshed-time")

                result = {
                    "stock code": stock["stock code"],
                    "company name": stock["company name"],
                    "price": price_text,
                    "timestamp": timestamp.strip() if timestamp else None,
                    "status": "success",
                    "error": None,
                }

            except Exception as e:
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

        return result

    async def crawl_all(self, stocks: list[dict]) -> list[dict]:
        tasks = [self.get_stock_data(stock) for stock in stocks]
        return await asyncio.gather(*tasks)
