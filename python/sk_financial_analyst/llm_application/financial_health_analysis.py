"""This class generates a financial health analysis of a company."""

import pathlib
import sys
import logging 

sys.path.append(str(pathlib.Path(__file__).parent))
from assistants import assistants as assistants  # noqa: E402


class FinancialHealthAnalysis:
    """This class encapsulate assistants to generate a final report."""

    def __init__(
        self,
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
    ):
        """Initialize parameters."""
        self.aoai_token = aoai_token
        self.aoai_base_endpoint = aoai_base_endpoint
        self.aoai_api_version = aoai_api_version
        self.bing_search_endpoint = bing_search_endpoint
        self.bing_search_api_key = bing_search_api_key
        self.news_analyst_model = news_analyst_model
        self.financial_analyst_model = financial_analyst_model
        self.max_news = max_news
        self.sec_identity = sec_identity
        self.structured_report_generator_model = structured_report_generator_model

    async def __call__(self, stock_ticker: str):
        """
        Run reports one by one.

        Generate a consolidated report at the end.
        """
        reports = {}

        # Create the news analyst assistant
        news_analyst = assistants.NewsAnalyst(
            aoai_token=self.aoai_token,
            aoai_base_endpoint=self.aoai_base_endpoint,
            llm_deployment_name=self.news_analyst_model,
            bing_search_api_key=self.bing_search_api_key,
            bing_search_endpoint=self.bing_search_endpoint,
            max_news=self.max_news,
        )

        # Get the news report for the stock ticker
        reports["news_report"] = await news_analyst.get_news_report(stock_ticker=stock_ticker)

        # Create the financial analyst assistant
        financial_analyst = assistants.FinancialAnalyst(
            aoai_token=self.aoai_token,
            aoai_base_endpoint=self.aoai_base_endpoint,
            llm_deployment_name=self.financial_analyst_model,
            sec_identity=self.sec_identity,
        )
        logging.debug(f"FinancialAnalyst state: {financial_analyst.__dict__}")

        # Get the financial reports for the stock ticker

        report_type = "balance_sheet"
        balance_sheet_report_metrics = """
            current ratio,
            quick ratio,
            working capital,
            debt to equity ratio
        """

        logging.debug(f"Requesting balance_sheet report for {stock_ticker} with metrics: {balance_sheet_report_metrics}")
        reports["balance_sheet_report"] = await financial_analyst.get_financial_report(
            stock_ticker=stock_ticker, report_type=report_type, report_metrics=balance_sheet_report_metrics
        )

        report_type = "income"
        income_report_metrics = """
            gross margin,
            profit margin,
            operating margin,
            basic earnings per share,
            basic price to earnings ratio,
            return on equity
        """
        logging.debug(f"Requesting income report for {stock_ticker} with metrics: {income_report_metrics}")
        reports["income_report"] = await financial_analyst.get_financial_report(
            stock_ticker=stock_ticker, report_type=report_type, report_metrics=income_report_metrics
        )

        report_type = "cash_flow"
        cash_flow_report_metrics = """
            cash flow per share,
            free cash flow,
            cash flow to debt ratio
        """
        logging.debug(f"Requesting cash_flow report for {stock_ticker} with metrics: {cash_flow_report_metrics}")
        reports["cash_flow_report"] = await financial_analyst.get_financial_report(
            stock_ticker=stock_ticker, report_type=report_type, report_metrics=cash_flow_report_metrics
        )

        # Create the report generator assistant
        structured_report_generator = assistants.StructuredReportGenerator(
            aoai_token=self.aoai_token,
            aoai_base_endpoint=self.aoai_base_endpoint,
            llm_deployment_name=self.structured_report_generator_model,
            aoai_api_version=self.aoai_api_version,
        )

        # Generate the structured consolidated report
        reports["consolidated_report"] = await structured_report_generator.get_consolidated_report(
            balance_sheet_report=reports["balance_sheet_report"],
            income_report=reports["income_report"],
            cash_flow_report=reports["cash_flow_report"],
            news_report=reports["news_report"],
        )

        return reports
