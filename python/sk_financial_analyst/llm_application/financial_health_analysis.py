"""This script generates a financial health analysis of a company."""

import asyncio
import os
import argparse
from pprint import pprint
from dotenv import load_dotenv

from assistants import assistants as assistants
from utils import report_generator
from utils import config_reader

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


async def main(stock_ticker, output_folder):
    """Generate a financial health analysis of a company."""
    # Load the environment variables from the .env file
    load_dotenv()
    
    # Load the configuration data
    config_data = config_reader.load_yaml("./llm_application/config.yaml")

    # Get values from the configuration data
    auth_provider_endpoint = config_reader.get_value_by_name(
        config_data,
        "financial_health_analysis",
        "auth_provider_endpoint"
    )
    key_vault_url = config_reader.get_value_by_name(
        config_data,
        "financial_health_analysis",
        "key_vault_url"
    )
    news_analyst_model = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "news_analyst",
        "llm_deployment_name"
    )
    bing_search_endpoint = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "news_analyst",
        "bing_search_endpoint"
    )
    max_news = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "news_analyst",
        "max_news"
    )
    financial_analyst_model = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "financial_analyst",
        "llm_deployment_name"
    )
    structured_report_generator_model = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "structured_report_generator",
        "llm_deployment_name"
    )
    aoai_api_version = config_reader.get_value_by_name(
        config_data,
        "assistants",
        "structured_report_generator",
        "aoai_api_version"
    )

    # Get Azure OpenAI authentication token
    credential = DefaultAzureCredential()
    aoai_token = credential.\
        get_token(auth_provider_endpoint).token

    # Get Azure OpenAI deployment name from Azure Key Vault
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    aoai_base_endpoint = client.get_secret("aoai-base-endpoint").value

    # Get Bing Search key and SEC Identity from Azure Key Vault
    bing_search_api_key = client.get_secret("bing-search-api-key").value
    sec_identity = client.get_secret("sec-identity").value

    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create the news analyst assistant
    news_analyst = assistants.NewsAnalyst(
        aoai_token=aoai_token,
        aoai_base_endpoint=aoai_base_endpoint,
        llm_deployment_name=news_analyst_model,
        bing_search_api_key=bing_search_api_key,
        bing_search_endpoint=bing_search_endpoint,
        max_news=max_news
    )

    # Get the news report for the stock ticker
    news_report = await news_analyst.get_news_report(stock_ticker=stock_ticker)
    print("NEWS REPORT\n-----------")
    print(news_report)
    print("==================================================================")

    # Create the financial analyst assistant
    financial_analyst = assistants.FinancialAnalyst(
        aoai_token=aoai_token,
        aoai_base_endpoint=aoai_base_endpoint,
        llm_deployment_name=financial_analyst_model,
        sec_identity=sec_identity
    )

    # Get the financial reports for the stock ticker
    report_type = "balance_sheet"
    balance_sheet_report_metrics = """
        current ratio,
        quick ratio,
        working capital,
        debt to equity ratio
    """
    balance_sheet_report = await financial_analyst.get_financial_report(
        stock_ticker=stock_ticker,
        report_type=report_type,
        report_metrics=balance_sheet_report_metrics
    )
    print("BALANCE SHEET REPORT\n--------------------")
    print(balance_sheet_report)
    print("==================================================================")

    report_type = "income"
    income_report_metrics = """
        gross margin,
        profit margin,
        operating margin,
        earnings per share,
        price to earnings ratio,
        return on equity
    """
    income_report = await financial_analyst.get_financial_report(
        stock_ticker=stock_ticker,
        report_type=report_type,
        report_metrics=income_report_metrics
    )
    print("INCOME REPORT\n-------------")
    print(income_report)
    print("==================================================================")

    report_type = "cash_flow"
    cash_flow_report_metrics = """
        cash flow per share,
        free cash flow,
        cash flow to debt ratio
    """
    cash_flow_report = await financial_analyst.get_financial_report(
        stock_ticker=stock_ticker,
        report_type=report_type,
        report_metrics=cash_flow_report_metrics
    )
    print("CASH FLOW REPORT\n----------------")
    print(cash_flow_report)
    print("==================================================================")

    # Create the report generator assistant
    structured_report_generator = assistants.StructuredReportGenerator(
        aoai_token=aoai_token,
        aoai_base_endpoint=aoai_base_endpoint,
        llm_deployment_name=structured_report_generator_model,
        aoai_api_version=aoai_api_version
    )

    # Generate the structured consolidated report
    consolidated_report = \
        await structured_report_generator.get_consolidated_report(
            balance_sheet_report=balance_sheet_report,
            income_report=income_report,
            cash_flow_report=cash_flow_report,
            news_report=news_report
        )
    print("CONSOLIDATED REPORT\n-------------------")
    pprint(consolidated_report)
    print("==================================================================")

    # Save the consolidated report to a JSON file
    consolidated_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_consolidated_report.json"
    )
    with open(consolidated_report_file, "w") as file:
        file.write(consolidated_report)

    # Generate the markdown report
    markdown_report = report_generator.json_to_markdown_report(
        consolidated_report_file
    )
    print("MARKDOWN REPORT\n---------------")
    print(markdown_report)
    print("==================================================================")

    # Save the markdown report to a file
    markdown_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_consolidated_report.md"
    )
    with open(markdown_report_file, "w") as file:
        file.write(markdown_report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
            Script to generate a financial health analysis of a company.
        """
    )
    parser.add_argument(
        "stock_ticker",
        type=str,
        nargs="?",
        default="MSFT",
        help="The stock ticker symbol to generate the analysis for."
    )
    parser.add_argument(
        "output_folder",
        type=str,
        nargs="?",
        default="./data/outputs",
        help="The folder where the output data will be saved."
    )
    args = parser.parse_args()
    asyncio.run(main(args.stock_ticker, args.output_folder))
