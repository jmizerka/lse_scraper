import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from core.csv_handler import CSVHandler
from core.crawler import Crawler
from core.stock_processor import StocksProcessor
from utils.logger_setup import setup_logging

setup_logging("api")
logger = logging.getLogger(__name__)
app = FastAPI(title="Stock Processor API")


@app.post("/process_csv", summary="Upload CSV and get processed CSV in response")
async def process_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    try:
        content = await file.read()
        stocks = CSVHandler.read_csv(content)
        logger.info("Received CSV with %s rows", len(stocks))
        async with Crawler(max_concurrent=5) as crawler:
            processor = StocksProcessor(crawler)
            results = await processor.process_stocks(stocks)
        csv_bytes = CSVHandler.write_csv(results, as_bytes=True)
        return StreamingResponse(
            csv_bytes, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=stocks_result.csv"}
        )

    except Exception as e:
        logger.exception("Error processing CSV: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}
