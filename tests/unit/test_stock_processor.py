import pytest
from core.stock_processor import StocksProcessor


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
