import logging
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from common.configurator import config_reader
from fastapi import APIRouter, FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.trace import SpanKind
from sk_financial_analyst.llm_application.financial_health_analysis import FinancialHealthAnalysis

# Load the configuration data
config_data = config_reader.load_yaml("./sk_financial_analyst/config/config.yaml")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# from llm_application import financial_health_analysis

app = FastAPI(title="Financial Health Analysis API", version="1.0.0")
router = APIRouter()

logger.info("Otel configuration started..")

OpenAIInstrumentor().instrument()
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)
logger.info("Otel configuration successful..")


@router.get("/generate_financial_report/{stock_ticker}", summary="Generate Financial Report")
async def run_financial_health_analysis(stock_ticker: str):
    try:
        with tracer.start_as_current_span("run_financial_analysis_report", kind=SpanKind.SERVER) as span:
            logger.info("Starting finacial report generation..")

            key_vault_url = os.environ.get("KEY_VAULT_URL")

            # Get values from the configuration data
            auth_provider_endpoint = config_reader.get_value_by_name(
                config_data, "financial_health_analysis", "auth_provider_endpoint"
            )
            news_analyst_model = os.environ.get("NEWS_ANALYST_MODEL_NAME")

            span.set_attribute("news_analyst_model", news_analyst_model)

            bing_search_endpoint = config_reader.get_value_by_name(
                config_data, "assistants", "news_analyst", "bing_search_endpoint"
            )
            max_news = os.environ.get("MAX_NEWS")
            financial_analyst_model = os.environ.get("FINANCIAL_ANALYST_MODEL_NAME")
            structured_report_generator_model = os.environ.get("REPORT_GENERATOR_MODEL_NAME")

            span.set_attribute("news_analyst_model", financial_analyst_model)

            aoai_api_version = config_reader.get_value_by_name(
                config_data, "assistants", "structured_report_generator", "aoai_api_version"
            )
            span.set_attribute("aoai_api_version", aoai_api_version)

            with tracer.start_as_current_span("DefaultAzureCredential & SecretClient call"):
                managed_identity_client_id = os.environ.get("AZURE_CLIENT_ID")
                credential_kwargs = {
                    "exclude_workload_identity_credential": True,
                    "exclude_environment_credential": True,
                    "logging_enable": True,
                }
                if managed_identity_client_id is None:
                    credential_kwargs["exclude_managed_identity_credential"] = True
                else:
                    credential_kwargs["managed_identity_client_id"] = managed_identity_client_id
                credential = DefaultAzureCredential(**credential_kwargs)
                aoai_token = credential.get_token(auth_provider_endpoint).token

                # Get Azure OpenAI deployment name from Azure Key Vault
                client = SecretClient(vault_url=key_vault_url, credential=credential)
                aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value

                # Get Bing Search key from Azure Key Vault
                bing_search_api_key = client.get_secret("bing-search-api-key").value

                # Get SEC identity from Azure Key Vault
                sec_identity = client.get_secret("sec-identity").value

            with tracer.start_as_current_span("financial_health_analysis call.."):
                report = FinancialHealthAnalysis(
                    aoai_token,
                    aoai_base_endpoint,
                    aoai_api_version,
                    bing_search_endpoint,
                    bing_search_api_key,
                    news_analyst_model,
                    max_news,
                    financial_analyst_model,
                    sec_identity,
                    structured_report_generator_model,
                )

                generated_report = await report(stock_ticker)

                logger.info("Financial report generated successfully..")
                return generated_report
    except TimeoutError:
        return {"message:": f"Operation timeout during report generation of {stock_ticker}"}


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Financial Health Analysis API, a health endpoint!"}


app.include_router(router, prefix="/api", tags=["Financial Reports"])
