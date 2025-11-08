import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

from core.crawler import Crawler
from core.stocks_processor import StocksProcessor
from utils.logger_setup import setup_logging

setup_logging("api")
logger = logging.getLogger(__name__)
app = FastAPI(title="Stock Processor API")


@app.post("/process_csv", summary="Upload CSV and get processed CSV in response")
async def process_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        content = await file.read()
        df = pd.read_csv(BytesIO(content)).where(pd.notnull, None)
        stocks = df.to_dict(orient="records")
        logger.info(f"Received CSV with {len(stocks)} rows")
        async with Crawler(max_concurrent=5) as crawler:
            processor = StocksProcessor(crawler)
            results = await processor.process_stocks(stocks)
        output = pd.DataFrame(results)
        buffer = BytesIO()
        output.to_csv(buffer, index=False)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=stocks_result.csv"}
        )

    except Exception as e:
        logger.exception(f"Error processing CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}