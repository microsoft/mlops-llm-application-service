"""This script generates a financial health analysis of a company."""

import argparse
import asyncio
import json
import logging
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from common.configurator import config_reader, otel
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from sk_financial_analyst.llm_application.financial_health_analysis import FinancialHealthAnalysis
from sk_financial_analyst.utils import report_generator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)


async def generate_report(config_file, stock_ticker):
    """
    Generate a financial health analysis of a company.

    Args:
        config_file (str): The path to the configuration file.
        stock_ticker (str): The stock ticker symbol of the company.

    Returns:
        dict: The financial health analysis report.
    """
    # Load the configuration data
    config_data = config_reader.load_yaml(config_file)

    logger.info("Otel configuration started..")
    otel.config_otel()
    tracer = trace.get_tracer(__name__)
    logger.info("Otel configuration successful..")

    with tracer.start_as_current_span("financial_analysis_report", kind=SpanKind.SERVER) as span:
        # Get values from the configuration data
        auth_provider_endpoint = config_reader.get_value_by_name(
            config_data, "financial_health_analysis", "auth_provider_endpoint"
        )
        key_vault_url = config_reader.get_value_by_name(config_data, "financial_health_analysis", "key_vault_url")
        news_analyst_model = config_reader.get_value_by_name(
            config_data, "assistants", "news_analyst", "llm_deployment_name"
        )
        span.set_attribute("news_analyst_model", news_analyst_model)
        bing_search_endpoint = config_reader.get_value_by_name(
            config_data, "assistants", "news_analyst", "bing_search_endpoint"
        )
        max_news = config_reader.get_value_by_name(config_data, "assistants", "news_analyst", "max_news")
        financial_analyst_model = config_reader.get_value_by_name(
            config_data, "assistants", "financial_analyst", "llm_deployment_name"
        )
        span.set_attribute("financial_analyst_model", financial_analyst_model)
        structured_report_generator_model = config_reader.get_value_by_name(
            config_data,
            "assistants",
            "structured_report_generator",
            "llm_deployment_name",
        )
        aoai_api_version = config_reader.get_value_by_name(
            config_data, "assistants", "structured_report_generator", "aoai_api_version"
        )

        logger.info("aoi api version: %s", aoai_api_version)
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

            # invoke __call__ method to run report and return results back
            report_results = await report(stock_ticker)

            return report_results


async def main(stock_ticker, output_folder, save_intermediate_results, logging_enabled):
    """
    Generate a financial health analysis of a company and save results.

    Args:
        stock_ticker (str): The stock ticker symbol of the company.
        output_folder (str): The folder where the output data will be saved.
        save_intermediate_results (bool): Store intermediate results produced by agents.
        logging_enabled (bool): Enable logging.
    """
    if not logging_enabled:
        logging.disable(sys.maxsize)

    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate the report
    print(f"Generating financial health analysis for {stock_ticker}...")
    report_results = await generate_report("./sk_financial_analyst/config/config.yaml", stock_ticker)
    print(f"Financial health analysis for {stock_ticker} generated.")

    consolidated_report = json.loads(report_results["consolidated_report"])

    if save_intermediate_results:
        consolidated_report["intermediate_report"] = (
            report_results["news_report"]
            + report_results["balance_sheet_report"]
            + report_results["income_report"]
            + report_results["cash_flow_report"]
        )

    # Save the consolidated report to a JSON file
    consolidated_report_file = os.path.join(output_folder, f"{stock_ticker}_consolidated_report.json")
    with open(consolidated_report_file, "w") as fp:
        json.dump(consolidated_report, fp)

    # Generate the markdown report
    markdown_report = report_generator.json_to_markdown_report(consolidated_report_file)

    # Save the markdown report to a file
    markdown_report_file = os.path.join(output_folder, f"{stock_ticker}_consolidated_report.md")
    with open(markdown_report_file, "w") as file:
        file.write(markdown_report)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="""
            Script to generate a financial health analysis of a company.
        """
    )
    parser.add_argument(
        "--stock_ticker",
        type=str,
        nargs="?",
        default="MSFT",
        help="The stock ticker symbol to generate the analysis for.",
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        nargs="?",
        default="./sk_financial_analyst/data/outputs",
        help="The folder where the output data will be saved.",
    )
    parser.add_argument(
        "--save_intermediate_results",
        action="store_true",
        default=False,
        help="Store intermediate results produced by agents.",
    )

    parser.add_argument("--logging_enabled", action="store_true", default=False, help="Enable logging.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(
            main(
                args.stock_ticker,
                args.output_folder,
                args.save_intermediate_results,
                args.logging_enabled,
            )
        )
    except KeyboardInterrupt:
        logger.error("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
