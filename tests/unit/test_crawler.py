import pytest
from unittest.mock import AsyncMock
from core.crawler import Crawler


@pytest.mark.asyncio
async def test_build_url():
    crawler = Crawler()
    stock = {"company name": "Vodafone Group", "stock code": "VOD"}
    url = crawler._build_url(stock)
    assert url == "https://www.londonstockexchange.com/stock/VOD/vodafone-group/company-page"


@pytest.mark.asyncio
async def test_get_stock_data_failure(monkeypatch):
    crawler = Crawler(max_concurrent=1)
    fake_page = AsyncMock()
    fake_page.goto.side_effect = Exception("timeout")
    fake_page.close = AsyncMock()

    fake_browser = AsyncMock()
    fake_browser.new_page.return_value = fake_page
    crawler.browser = fake_browser

    stock = {"company name": "Vodafone", "stock code": "VOD"}
    result = await crawler.get_stock_data(stock)

    assert result["status"] == "failed"
    assert "timeout" in result["error"]
    fake_page.close.assert_called_once()


@pytest.mark.asyncio
async def test_crawl_all(monkeypatch):
    crawler = Crawler()
    mock_get = AsyncMock(
        side_effect=[
            {"company name": "A", "status": "success"},
            {"company name": "B", "status": "success"},
        ]
    )
    crawler.get_stock_data = mock_get

    stocks = [
        {"company name": "A", "stock code": "AAA"},
        {"company name": "B", "stock code": "BBB"},
    ]

    results = await crawler.crawl_all(stocks)
    assert len(results) == 2
    assert all(r["status"] == "success" for r in results)
    assert mock_get.call_count == 2
