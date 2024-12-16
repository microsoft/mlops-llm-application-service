"""This script generates a financial health analysis of a company."""

import argparse
import asyncio
import logging
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from common.configurator import config_reader
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from sk_financial_analyst.llm_application.financial_health_analysis import FinancialHealthAnalysis
from sk_financial_analyst.utils import report_generator
from sk_financial_analyst.utils.telemetry_configurator import TelemetryConfigurator


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

    # Get values from the configuration data
    auth_provider_endpoint = config_reader.get_value_by_name(
        config_data, "financial_health_analysis", "auth_provider_endpoint"
    )
    key_vault_url = config_reader.get_value_by_name(config_data, "financial_health_analysis", "key_vault_url")
    news_analyst_model = config_reader.get_value_by_name(
        config_data, "assistants", "news_analyst", "llm_deployment_name"
    )
    bing_search_endpoint = config_reader.get_value_by_name(
        config_data, "assistants", "news_analyst", "bing_search_endpoint"
    )
    max_news = config_reader.get_value_by_name(config_data, "assistants", "news_analyst", "max_news")
    financial_analyst_model = config_reader.get_value_by_name(
        config_data, "assistants", "financial_analyst", "llm_deployment_name"
    )
    structured_report_generator_model = config_reader.get_value_by_name(
        config_data, "assistants", "structured_report_generator", "llm_deployment_name"
    )
    aoai_api_version = config_reader.get_value_by_name(
        config_data, "assistants", "structured_report_generator", "aoai_api_version"
    )

    # Get Azure OpenAI authentication token
    credential = DefaultAzureCredential()
    aoai_token = credential.get_token(auth_provider_endpoint).token

    # Get Azure OpenAI deployment name from Azure Key Vault
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value

    # Get Bing Search key from Azure Key Vault
    bing_search_api_key = client.get_secret("bing-search-api-key").value

    # Get SEC identity from Azure Key Vault
    sec_identity = client.get_secret("sec-identity").value

    # Get Application Insights connection string from Azure Key Vault
    app_insights_connection_string = client.get_secret("app-insights-connection-string").value

    # Configure telemetry
    telemetry_configurator = TelemetryConfigurator(app_insights_connection_string)
    telemetry_configurator.set_up_logging()
    telemetry_configurator.set_up_metrics()
    tracer = telemetry_configurator.set_up_tracing()

    print("auth_provider_endpoint:", auth_provider_endpoint, flush=True)
    print("key_vault_url:", key_vault_url, flush=True)
    print("news_analyst_model:", news_analyst_model, flush=True)
    print("bing_search_endpoint:", bing_search_endpoint, flush=True)
    print("max_news:", max_news, flush=True)
    print("financial_analyst_model:", financial_analyst_model, flush=True)
    print(
        "structured_report_generator_model:",
        structured_report_generator_model,
        flush=True,
    )
    print("aoai_api_version:", aoai_api_version, flush=True)
    print("aoai_token:", aoai_token, flush=True)
    print("aoai_base_endpoint:", aoai_base_endpoint, flush=True)
    print("bing_search_api_key:", bing_search_api_key, flush=True)
    print("sec_identity:", sec_identity, flush=True)
    print("app_insights_connection_string:", app_insights_connection_string, flush=True)

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

    # invoke __call__ method to run report and return results back
    with tracer.start_as_current_span("financial_health_analysis"):
        report_results = await report(stock_ticker)

    return report_results


async def main(stock_ticker, output_folder, intermediate_data_folder, logging_enabled):
    """
    Generate a financial health analysis of a company and save results.

    Args:
        stock_ticker (str): The stock ticker symbol of the company.
        output_folder (str): The folder where the output data will be saved.
        intermediate_data_folder (str): The folder where the
            intermediate output data will be saved.
        logging_enabled (bool): Enable logging.
    """
    if not logging_enabled:
        logging.disable(sys.maxsize)

    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create the intermediate data folder if it does not exist
    if not os.path.exists(intermediate_data_folder):
        os.makedirs(intermediate_data_folder)

    # Generate the report
    print(f"Generating financial health analysis for {stock_ticker}...")
    report_results = await generate_report("sk_financial_analyst/config/config.yaml", stock_ticker)
    print(f"Financial health analysis for {stock_ticker} generated.")

    # Save the news report to a file
    news_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_news_report.txt")
    with open(news_report_file, "w") as file:
        file.write(report_results["news_report"])

    # Save the balance sheet report to a file
    balance_sheet_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_balance_sheet_report.txt")
    with open(balance_sheet_report_file, "w") as file:
        file.write(report_results["balance_sheet_report"])

    # Save the income report to a file
    income_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_income_report.txt")
    with open(income_report_file, "w") as file:
        file.write(report_results["income_report"])

    # Save the cash flow report to a file
    cash_flow_report_file = os.path.join(intermediate_data_folder, f"{stock_ticker}_cash_flow_report.txt")
    with open(cash_flow_report_file, "w") as file:
        file.write(report_results["cash_flow_report"])

    # Save the consolidated report to a JSON file
    consolidated_report_file = os.path.join(output_folder, f"{stock_ticker}_consolidated_report.json")
    with open(consolidated_report_file, "w") as file:
        file.write(report_results["consolidated_report"])

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
        "--intermediate_data_folder",
        type=str,
        nargs="?",
        default="./sk_financial_analyst/data/intermediate",
        help="The folder where the intermediate output data will be saved.",
    )
    parser.add_argument("--logging_enabled", action="store_true", default=False, help="Enable logging.")
    return parser.parse_args()


async def test_azure_chat_completion():
    try:
        key_vault_url = "https://llm-app-keyvault.vault.azure.net/"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)

        aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value
        aoai_api_key = client.get_secret("aoai-api-key").value
        aoai_deployment_name = client.get_secret("aoai-deployment-name").value
        aoai_api_version = client.get_secret("aoai-api-version").value

        print(f"aoai_base_endpoint: {aoai_base_endpoint}")
        print(f"aoai_api_key: {aoai_api_key}")
        print(f"aoai_deployment_name: {aoai_deployment_name}")
        print(f"aoai_api_version: {aoai_api_version}")

        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=aoai_deployment_name,
            endpoint=aoai_base_endpoint,
            api_key=aoai_api_key,
            api_version=aoai_api_version,
        )
        kernel.add_service(chat_completion)
        execution_settings = OpenAIChatPromptExecutionSettings()

        chat_completion_service_by_type = kernel.get_service(type=ChatCompletionClientBase)
        print(f"Chat Completion Service by Type: {chat_completion_service_by_type}")
        print(f"OpenAIChatPromptExecution Settings: {execution_settings}")
        print(f"ChatCompletion Attributes: {chat_completion.__dict__}")

        history = ChatHistory()
        history.add_system_message("You are a helpful story-writer assistant.")
        history.add_user_message("Tell me a story.")

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=None,  # Use default settings for simplicity
        )
        print(f"Chat completion result: {result.content}")
        return result.content

    except Exception as e:
        print(f"An error occurred during chat completion: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(test_azure_chat_completion())
        # asyncio.run(main(args.stock_ticker, args.output_folder, args.intermediate_data_folder, args.logging_enabled))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
