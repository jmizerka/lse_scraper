import pytest
import asyncio
from unittest.mock import patch
from app.core.csv_handler import CSVHandler
from app.cli.cli_adapter import CLIAdapter
from app.cron.cron_adapter import CronAdapter
from app.watchdog.watchdog_adapter import WatcherAdapter
import os
import pandas as pd
import io
from httpx import ASGITransport, AsyncClient
from app.api.entrypoint import app


class MockCrawler:
    def __init__(self, max_concurrent):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return

    async def crawl_all(self, stocks):
        return [
            {
                "stock code": s["stock code"],
                "company name": s["company name"],
                "price": "100",
                "timestamp": "2025-01-01",
                "status": "success",
                "error": None,
            }
            for s in stocks
        ]


@pytest.mark.asyncio
@patch("app.cli.cli_adapter.Crawler", new=MockCrawler)
async def test_cli_adapter(tmp_path):
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"
    data = [{"company name": "A", "stock code": "AAA"}]
    CSVHandler.write_csv(data, path=input_csv)
    await CLIAdapter.run(str(input_csv), str(output_csv))
    result = CSVHandler.read_csv(output_csv)
    assert len(result) == 1
    assert result[0]["status"] == "success"


@pytest.mark.asyncio
@patch("app.cron.cron_adapter.Crawler", new=MockCrawler)
async def test_cron_adapter(tmp_path):
    input_csv = tmp_path / "stocks.csv"
    output_csv = tmp_path / "stocks_output.csv"
    data = [{"company name": "B", "stock code": "BBB"}]
    CSVHandler.write_csv(data, path=input_csv)
    adapter = CronAdapter(str(input_csv), str(output_csv))
    await adapter._process_file()
    result = CSVHandler.read_csv(output_csv)
    assert len(result) == 1
    assert result[0]["status"] == "success"


@pytest.mark.asyncio
@patch("app.watchdog.watchdog_adapter.Crawler", new=MockCrawler)
async def test_watcher_adapter(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    adapter = WatcherAdapter(str(input_dir), str(output_dir))
    csv_file = input_dir / "test.csv"
    data = [{"company name": "C", "stock code": "CCC"}]
    CSVHandler.write_csv(data, path=csv_file)
    await adapter._process_file(str(csv_file))
    files = os.listdir(output_dir)
    assert len(files) == 1
    result = CSVHandler.read_csv(output_dir / files[0])
    assert len(result) == 1
    assert result[0]["status"] == "success"


@pytest.mark.asyncio
@patch("app.api.entrypoint.Crawler", new=MockCrawler)
async def test_api_process_csv_mocked():
    df = pd.DataFrame(
        [
            {"company name": "Test Co", "stock code": "TEST1"},
            {"company name": "Another Co", "stock code": "TEST2"},
        ]
    )
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("stocks.csv", buffer, "text/csv")}
        response = await client.post("/process_csv", files=files)

    assert response.status_code == 200
    content = response.content.decode()
    assert "TEST1" in content
    assert "TEST2" in content


@pytest.mark.asyncio
@patch("app.api.entrypoint.Crawler", new=MockCrawler)
async def test_api_process_csv_non_csv():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("not_csv.txt", io.BytesIO(b"test data"), "text/plain")}
        response = await client.post("/process_csv", files=files)
    assert response.status_code == 400
    assert "Only CSV files are supported" in response.text


@pytest.mark.asyncio
@patch("app.cli.cli_adapter.Crawler", new=MockCrawler)
async def test_cli_adapter_corrupted_csv(tmp_path):
    input_csv = tmp_path / "bad.csv"
    input_csv.write_text("not,a,valid,csv\n,,")
    output_csv = tmp_path / "out.csv"
    with pytest.raises(ValueError):
        await CLIAdapter.run(str(input_csv), str(output_csv))


@pytest.mark.asyncio
@patch("app.watchdog.watchdog_adapter.Crawler", new=MockCrawler)
async def test_watcher_multiple_files(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    adapter = WatcherAdapter(str(input_dir), str(output_dir))
    for i in range(3):
        csv_file = input_dir / f"file_{i}.csv"
        CSVHandler.write_csv([{"company name": f"Co{i}", "stock code": f"STK{i}"}], path=csv_file)
        await adapter._process_file(str(csv_file))
        await asyncio.sleep(1)

    files = os.listdir(output_dir)
    assert len(files) == 3
    for f in files:
        result = CSVHandler.read_csv(output_dir / f)
        assert len(result) == 1
        assert result[0]["status"] == "success"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
