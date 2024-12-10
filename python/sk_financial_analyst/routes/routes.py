import asyncio
import logging

from fastapi import APIRouter, FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from sk_financial_analyst.executors import single_item_executor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from llm_application import financial_health_analysis

app = FastAPI(title="Financial Health Analysis API", version="1.0.0")
router = APIRouter()
OpenAIInstrumentor().instrument()
FastAPIInstrumentor.instrument_app(app)


@router.get("/generate_financial_report/{stock_ticker}", summary="Generate Financial Report")
async def run_financial_health_analysis(stock_ticker: str):
    try:
        logger.info("Starting finacial report generation..")
        await asyncio.wait_for(
            single_item_executor.main(stock_ticker, "./data/outputs", "./data/intermediate", True), timeout=1200
        )  # 20m as timeout
        logger.info("Financial report generated successfully..")
        return {"message": f"Financial report successfully generated for {stock_ticker}"}
    except TimeoutError:
        return {"message:": f"Operation timeout during report generation of {stock_ticker}"}


app.include_router(router, prefix="/api", tags=["Financial Reports"])


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Financial Health Analysis API, a health endpoint!"}
