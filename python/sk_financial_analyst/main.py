import logging

from fastapi import APIRouter, FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from llm_application import financial_health_analysis

app = FastAPI(title="Financial Health Analysis API", version="1.0.0")
router = APIRouter()


@router.get("/generate_financial_report/{stock_ticker}", summary="Generate Financial Report")
async def run_financial_health_analysis(stock_ticker: str):
    # financial_health_analysis.run(stock_ticker)
    logging.info("Financial report analysis started...")
    return {"message": f"Financial report successfully generated for {stock_ticker}"}


app.include_router(router, prefix="/api", tags=["Financial Reports"])


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Financial Health Analysis API, a health endpoint!"}
