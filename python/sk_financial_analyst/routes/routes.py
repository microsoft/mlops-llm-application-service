import asyncio
import logging

from fastapi import APIRouter, FastAPI
from sk_financial_analyst.executors import single_item_executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from llm_application import financial_health_analysis

app = FastAPI(title="Financial Health Analysis API", version="1.0.0")
router = APIRouter()


@router.get("/generate_financial_report/{stock_ticker}", summary="Generate Financial Report")
async def run_financial_health_analysis(stock_ticker: str):
    try:
        await asyncio.wait_for(
            single_item_executor.main(stock_ticker, "./data/outputs", "./data/intermediate"), timeout=1200
        )  # 20m as timeout
        return {"message": f"Financial report successfully generated for {stock_ticker}"}
    except TimeoutError:
        return {"message:": f"Operation timeout during report generation of {stock_ticker}"}


app.include_router(router, prefix="/api", tags=["Financial Reports"])


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Financial Health Analysis API, a health endpoint!"}
