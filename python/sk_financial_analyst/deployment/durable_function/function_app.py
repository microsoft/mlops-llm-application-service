"""Durable Azure Function Implementation."""

import logging
import os

import azure.durable_functions as df
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from llm_application.financial_health_analysis import FinancialHealthAnalysis

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route("Health", auth_level=func.AuthLevel.FUNCTION)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Check health of the function."""
    version = 1
    logging.info(f"Health check version {version}")
    return func.HttpResponse(f"This function executed successfully with version {version}.", status_code=200)


@app.route(route="GetReportAsync", auth_level=func.AuthLevel.FUNCTION)
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client):
    """Trigger the orchestrator and pass a parameter from the client."""
    try:
        req_body = req.get_json()
        if not isinstance(req_body, dict):
            return func.HttpResponse("String has been passed but json is expected", status_code=400)
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    stock_ticker = req_body.get("stock_ticker")

    if stock_ticker:
        instance_id = await client.start_new("report_orchestrator", client_input={"stock_ticker": stock_ticker})
        response = client.create_check_status_response(req, instance_id)
        return response
    else:
        return func.HttpResponse(
            "stock_ticker parameter have not been provided.",
            status_code=200,
        )


@app.orchestration_trigger(context_name="context")
def report_orchestrator(context: df.DurableOrchestrationContext):
    """Orchestrate the execution of the report."""
    logging.info("Start orchestrator")
    stock_ticker = context.get_input()["stock_ticker"]
    result = yield context.call_activity("generate_report", stock_ticker)
    logging.info("Stop orchestrator")
    return result


@app.activity_trigger(input_name="stock")
async def generate_report(stock):
    """Implement activity to invoke LLM App with needed parameters."""
    managed_identity_client_id = os.environ.get("AzureWebJobsStorage__clientId")
    key_vault_url = os.environ.get("KEY_VAULT_URL")

    # Get values from the configuration data
    auth_provider_endpoint = os.environ.get("AUTH_PROVIDER_ENDPOINT")
    news_analyst_model = os.environ.get("NEWS_ANALYST_MODEL_NAME")
    bing_search_endpoint = os.environ.get("BING_SEARCH_ENDPOINT")
    max_news = os.environ.get("MAX_NEWS")
    financial_analyst_model = os.environ.get("FINANCIAL_ANALYST_MODEL_NAME")
    structured_report_generator_model = os.environ.get("REPORT_GENERATOR_MODEL_NAME")
    aoai_api_version = os.environ.get("AOAI_API_VERSION")

    credential = DefaultAzureCredential(managed_identity_client_id=managed_identity_client_id)
    aoai_token = credential.get_token(auth_provider_endpoint).token

    # Get Azure OpenAI deployment name from Azure Key Vault
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value

    # Get Bing Search key from Azure Key Vault
    bing_search_api_key = client.get_secret("bing-search-api-key").value

    # Get SEC identity from Azure Key Vault
    sec_identity = client.get_secret("sec-identity").value

    # Get Application Insights connection string from Azure Key Vault
    # app_insights_connection_string = client.get_secret("app-insights-connection-string").value

    # Generate a report
    # Initialize report object first
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

    result = await report(stock)

    return result
