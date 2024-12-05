"""This script generates a financial health analysis of a company."""

import argparse
import asyncio
import logging
import os
import sys
from logging import getLogger
from pprint import pprint

# from azure.identity import (
#     AzureCliCredential,
#     ChainedTokenCredential,
#     ManagedIdentityCredential,
#     VisualStudioCodeCredential,
#     WorkloadIdentityCredential,
# )
from azure.identity import ChainedTokenCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from common.configurator import config_reader, otel
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from sk_financial_analyst.llm_application.financial_health_analysis import FinancialHealthAnalysis
from sk_financial_analyst.utils import report_generator

# from sk_financial_analyst.utils.telemetry_configurator import TelemetryConfigurator


async def main(stock_ticker, output_folder, intermediate_data_folder):
    """Generate a financial health analysis of a company."""
    config_file = "sk_financial_analyst/config/config.yaml"
    config_data = config_reader.load_yaml(config_file)
    logger = getLogger(__name__)
    logger.setLevel(logging.INFO)
    otel.config_otel()
    tracer = trace.get_tracer(__name__)
    # Load the configuration data
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
            config_data, "assistants", "structured_report_generator", "llm_deployment_name"
        )
        aoai_api_version = config_reader.get_value_by_name(
            config_data, "assistants", "structured_report_generator", "aoai_api_version"
        )
        span.set_attribute("aoai_api_version", aoai_api_version)

        with tracer.start_as_current_span("DefaultAzureCredential & SecretClient call"):
            client_id = os.environ.get("AZURE_CLIENT_ID")
            print("client id >>>>>" + client_id)
            # Get Azure OpenAI authentication token, ManagedIdentityCredential requires AZURE_CLIENT_ID to be set
            credential = ChainedTokenCredential(
                # AzureCliCredential(),
                # VisualStudioCodeCredential(),
                ManagedIdentityCredential(client_id=client_id)
                # WorkloadIdentityCredential(),
            )
            aoai_token = credential.get_token(auth_provider_endpoint).token

            # Get Azure OpenAI deployment name from Azure Key Vault
            client = SecretClient(vault_url=key_vault_url, credential=credential)
            aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value

            # Get Bing Search key from Azure Key Vault
            bing_search_api_key = client.get_secret("bing-search-api-key").value

            # Get SEC identity from Azure Key Vault
            sec_identity = client.get_secret("sec-identity").value

        with tracer.start_as_current_span("Generate Financial Health Analysis report"):
            # Create the output folder if it does not exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Create the intermediate data folder if it does not exist
            if not os.path.exists(intermediate_data_folder):
                os.makedirs(intermediate_data_folder)

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

            report_results = await report(stock_ticker)

        # invoke __call__ method to run report and return results back
        with tracer.start_as_current_span("save_report"):

            # Save the news report to a file
            news_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_news_report.txt")
            with open(news_report_file, "w") as file:
                file.write(report_results["news_report"])
            logger.info("NEWS REPORT\n-----------")
            print(report_results["news_report"])
            print("==================================================================")

            # Save the balance sheet report to a file
            balance_sheet_report_file = os.path.join(
                intermediate_data_folder, f"{stock_ticker}_balance_sheet_report.txt"
            )
            with open(balance_sheet_report_file, "w") as file:
                file.write(report_results["balance_sheet_report"])
            logger.info("BALANCE SHEET REPORT\n--------------------")
            print(report_results["balance_sheet_report"])
            print("==================================================================")

            # Save the income report to a file
            income_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_income_report.txt")
            with open(income_report_file, "w") as file:
                file.write(report_results["income_report"])
            logger.info("INCOME REPORT\n-------------")
            print(report_results["income_report"])
            print("==================================================================")

            # Save the cash flow report to a file
            cash_flow_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_cash_flow_report.txt")
            with open(cash_flow_report_file, "w") as file:
                file.write(report_results["cash_flow_report"])
            print("CASH FLOW REPORT\n----------------")
            print(report_results["cash_flow_report"])
            print("==================================================================")

            logger.info("CONSOLIDATED REPORT\n-------------------")
            pprint(report_results["consolidated_report"])
            print("==================================================================")

            # Save the consolidated report to a JSON file
            consolidated_report_file = os.path.join(output_folder, f"{stock_ticker}_consolidated_report.json")
            with open(consolidated_report_file, "w") as file:
                file.write(report_results["consolidated_report"])

        with tracer.start_as_current_span("json to markdown report"):
            # Generate the markdown report
            markdown_report = report_generator.json_to_markdown_report(consolidated_report_file)
            logger.info("MARKDOWN REPORT\n---------------")
            print(markdown_report)
            print("==================================================================")

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
        "--intermediate_data_folder",
        type=str,
        nargs="?",
        default="./sk_financial_analyst/data/intermediate",
        help="The folder where the intermediate output data will be saved.",
    )
    parser.add_argument("--logging_enabled", action="store_true", default=False, help="Enable logging.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(main(args.stock_ticker, args.output_folder, args.intermediate_data_folder, args.logging_enabled))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
