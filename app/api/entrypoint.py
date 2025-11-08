"""
Stock Processor API
-------------------
This module defines a FastAPI-based REST API for processing stock data from uploaded CSV files.

Main Features:
- Accepts a CSV upload containing stock symbols and related information.
- Crawls real-time or historical stock data using an asynchronous crawler.
- Processes the data with a stock processor.
- Returns a processed CSV file as a downloadable response.
- Includes a simple health check endpoint.

"""

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
    """
    Process an uploaded CSV file containing stock information and return the processed data.

    This endpoint accepts a CSV file upload containing stock tickers.
    It reads the file, processes each stock entry asynchronously using a crawler, and
    returns a new CSV file containing the last known price along with a timestamp.

    The process includes:
    - Validating the file format (must be a `.csv` file)
    - Reading and parsing the CSV data into a structured format
    - Crawling and processing each stock concurrently
    - Writing the enriched/processed data back to CSV and streaming it in the response

    Args:
        file (UploadFile): The uploaded CSV file. Must have a `.csv` extension.

    Returns:
        StreamingResponse: A downloadable CSV file (`stocks_result.csv`) containing the processed data.

    Raises:
        HTTPException:
            - 400: If the uploaded file is not a CSV file.
            - 500: If any unexpected error occurs during processing (e.g., crawling or parsing failure).
    """
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
