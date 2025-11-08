import pytest
from app.core.stock_processor import StocksProcessor


@pytest.mark.asyncio
async def test_process_stocks_success():
    class DummyCrawler:
        async def crawl_all(self, stocks):
            return [{"company name": s["company name"], "status": "success"} for s in stocks]

    stocks = [{"company name": "Vodafone", "stock code": "VOD"}]
    processor = StocksProcessor(DummyCrawler())
    result = await processor.process_stocks(stocks)

    assert len(result) == 1
    assert result[0]["status"] == "success"


@pytest.mark.asyncio
async def test_process_stocks_failure(monkeypatch):
    class BadCrawler:
        async def crawl_all(self, stocks):
            raise Exception("crash")

    processor = StocksProcessor(BadCrawler())
    result = await processor.process_stocks([{"company name": "Vodafone"}])
    assert result == []


@pytest.mark.asyncio
async def test_process_stocks_partial_success(monkeypatch):
    class MixedCrawler:
        async def crawl_all(self, stocks):
            return [
                {"company name": "Vodafone", "stock code": "V", "status": "success"},
                {"company name": "BT", "stock code": "BT", "status": "failed", "error": "timeout"},
            ]

    processor = StocksProcessor(MixedCrawler())
    result = await processor.process_stocks([{"company name": "Vodafone"}, {"company name": "BT"}])
    assert len(result) == 1
