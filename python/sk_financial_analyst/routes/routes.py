"""Routes for the financial analysis microservice."""

import asyncio
import logging
from fastapi import APIRouter, FastAPI
from sk_financial_analyst.executors import single_item_executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from llm_application import financial_health_analysis

app = FastAPI(title="Financial Health Analysis API", version="1.0.0")
router = APIRouter()


@router.get(
    "/generate_financial_report/{stock_ticker}", summary="Generate Financial Report"
)
async def run_financial_health_analysis(stock_ticker: str):
    """
    Generate a financial health report asynchronously.

    Args:
        stock_ticker (str): The ticker symbol for the stock.

    Returns:
        dict: A success message after generating the financial report.
    """
    try:
        await asyncio.wait_for(
            single_item_executor.main(
                stock_ticker, "./data/outputs", "./data/intermediate", True
            ),
            timeout=1200,
        )  # 20m as timeout
        return {
            "message": f"Financial report successfully generated for {stock_ticker}"
        }
    except TimeoutError:
        return {
            "message:": f"Operation timeout during report generation of {stock_ticker}"
        }


app.include_router(router, prefix="/api", tags=["Financial Reports"])


@app.get("/", summary="Root Endpoint")
def read_root():
    """
    Root endpoint for the financial health analysis API.

    Returns:
        dict: A welcome message.
    """
    return {
        "message": "Welcome to the Financial Health Analysis API, a health endpoint!"
    }
