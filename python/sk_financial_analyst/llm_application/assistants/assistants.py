"""
This module contains classes for implementing Semantic Kernel assistants.

The assistants are implemented with Semantic Kernel and are used to perform
analysis of financial statements from publc companies and generate a
consolidated report.
"""

import logging

from assistants.data_models import ConsolidatedReport
from plugins import plugins as plugins
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.utils.logging import setup_logging


class NewsAnalyst:
    """A class used to perform financial analysis of news articles."""

    def __init__(
        self, aoai_token, aoai_base_endpoint, llm_deployment_name, bing_search_api_key, bing_search_endpoint, max_news
    ):
        """Initialize the NewsAnalyst class."""
        self.aoai_token = aoai_token
        self.aoai_base_endpoint = aoai_base_endpoint
        self.llm_deployment_name = llm_deployment_name
        self.bing_search_api_key = bing_search_api_key
        self.bing_search_endpoint = bing_search_endpoint
        self.max_news = max_news
        print(f"assistants NewsAnalyst aoai_token: {aoai_token}", flush=True)
        print(f"assistants NewsAnalyst aoai_base_endpoint: {aoai_base_endpoint}", flush=True)
        print(f"assistants NewsAnalyst llm_deployment_name: {llm_deployment_name}", flush=True)

    async def get_news_report(self, stock_ticker):
        """Generate the financial analysis of news articles."""
        # Define system and user messages
        system_message = """
        You are a stock market financial analyst.
        You are specialized in identifying and analyzing sentiment signals
        in financial news articles.
        """
        user_message = f"""
        You are given a list of news articles,
        most of them related to the {stock_ticker} stock ticker.
        You task is to analyze the news articles to determine whether
        they are bullish or bearish for the {stock_ticker} stock ticker.
        You can disregard the news articles that you think are not relevant
        for this analysis.
        Your response should be a rubrik regarding the overall sentiment
        of the news articles, as bullish, bearish, or mixed,
        and why you arrived at that conclusion.
        """

        # Initialize the kernel
        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=self.llm_deployment_name, endpoint=self.aoai_base_endpoint, api_key=self.aoai_token
        )
        kernel.add_service(chat_completion)
        print(f"NewsAnalyst Kernel state: {kernel.__dict__}", flush=True)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Add the NewsPlugin to the kernel
        kernel.add_plugin(
            plugins.NewsPlugin(
                bing_search_api_key=self.bing_search_api_key,
                bing_search_endpoint=self.bing_search_endpoint,
                max_news=self.max_news,
            ),
            plugin_name="NewsPlugin",
        )

        # Enable planning
        execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True, filters={})

        # Set the chat history
        history = ChatHistory()
        history.add_system_message(system_message)
        history.add_user_message(user_message)

        # Get the response from the model
        while len(history.messages) < 4:
            result = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )

        return result.content


class FinancialAnalyst:
    """A class used to perform analysis of financial statements."""

    def __init__(self, aoai_token, aoai_base_endpoint, llm_deployment_name, sec_identity):
        """Initialize the FinancialAnalyst class."""
        self.aoai_token = aoai_token
        self.aoai_base_endpoint = aoai_base_endpoint
        self.llm_deployment_name = llm_deployment_name
        self.sec_identity = sec_identity

        print(f"assistants FinancialAnalyst aoai_token: {aoai_token}", flush=True)
        print(f"assistants FinancialAnalyst aoai_base_endpoint: {aoai_base_endpoint}", flush=True)
        print(f"assistants FinancialAnalyst llm_deployment_name: {llm_deployment_name}", flush=True)

    async def get_financial_report(self, stock_ticker, report_type, report_metrics):
        """Generate  the analysis of financial statements."""
        # Define system and user messages
        system_message = """
        You are a stock market financial analyst.
        You are specialized in analyzing the financial health of a company,
        by using the financial statements of the company and computing
        financial metrics derived from the financial statements.
        """
        user_message = f"""
        Analyze the financial health of {stock_ticker}, from the perspective of
        its financial statement of the type {report_type}.
        Calculate the following metrics,
        providing your interpretation of the results:

        {report_metrics}

        **MAKE SURE** to calculate matrics for all date periods provided
        in the financial statement.

        When analyzing a financial statement of type 'cash_flow',
        you should also get the corresponding 'balance_sheet' statement,
        to be able to compute all asked metrics.

        When analyzing a financial statement of type 'income', you
        should also get the corresponding statement of type 'balance_sheet',
        to be able to compute all asked metrics,
        plus the latest stock price for the {stock_ticker} stock ticker.
        """

        if not stock_ticker or not report_type:
            raise ValueError("Both 'ticker' and 'report_type' arguments are required.")
        print(f"assistants.py get_financial_report stock_ticker: {stock_ticker}, get_financial_report report_type: {report_type}", flush=True)

        # Initialize the kernel
        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=self.llm_deployment_name, endpoint=self.aoai_base_endpoint, api_key=self.aoai_token
        )
        kernel.add_service(chat_completion)
        print(f"Kernel state Financial chat_completion: {kernel.__dict__}", flush=True)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Add the FinancialStatementsPlugin to the kernel
        kernel.add_plugin(
            plugins.FinancialStatementsPlugin(sec_identity=self.sec_identity), plugin_name="FinancialStatementsPlugin"
        )
        print(f"Kernel state Financial after FinancialStatementsPlugin: {kernel.__dict__}", flush=True)
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Add the StockPricePlugin to the kernel
        kernel.add_plugin(plugins.StockPricePlugin(), plugin_name="StockPricePlugin")
        logging.getLogger("kernel").setLevel(logging.DEBUG)
        print(f"Kernel state Financial after StockPricePlugin: {kernel.__dict__}", flush=True)

        # Enable planning
        execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True, filters={})

        # Set the chat history
        history = ChatHistory()
        history.add_system_message(system_message)
        history.add_user_message(user_message)

        # Get the response from the model
        try:
            print(f"Calling get_chat_message_content", flush=True)
            print(f"Chat history: {history.__dict__}", flush=True)
            print(f"Execution settings: {execution_settings.__dict__}", flush=True)
            result = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )
            print(f"Chat completion result: {result.content}")
            return result.content
        except Exception as ex:
            print(f"Chat completion failed with Exception: {ex} Location (assistants.py).", flush=True)
            raise


class StructuredReportGenerator:
    """A class used to generate a consolidated financial report."""

    def __init__(self, aoai_token, aoai_base_endpoint, llm_deployment_name, aoai_api_version):
        """Initialize the ReportGenerator class."""
        self.aoai_token = aoai_token
        self.aoai_base_endpoint = aoai_base_endpoint
        self.llm_deployment_name = llm_deployment_name
        self.aoai_api_version = aoai_api_version

    async def get_consolidated_report(self, balance_sheet_report, income_report, cash_flow_report, news_report):
        """Generate the consolidated financial analysis report."""
        # Define system and user messages
        system_message = """
            You are a stock market financial analyst.

            You are specialized in analyzing the overall
            financial health of a company.

            For your analysis, you take into consideration:
            - the perspective of the individual analysis
            of the company's quarterly financial statements.
            - the financial news analysis related to the company.
            """
        user_message = f"""
        Create an overall analysis report for the company,
        given the set of statement analysis, and financial news analysis below.

        Make sure to not repeat data from each given analysis
        and not to describe formulas in the report.

        Balance Sheet Statement Analysis:

        {balance_sheet_report}

        Income Statement Analysis:

        {income_report}

        Cash Flow Statement Analysis:

        {cash_flow_report}

        Financial News Analysis:

        {news_report}
        """

        # Initialize the kernel
        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=self.llm_deployment_name,
            endpoint=self.aoai_base_endpoint,
            api_key=self.aoai_token,
            api_version=self.aoai_api_version,
        )
        kernel.add_service(chat_completion)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Set structured output
        execution_settings = AzureChatPromptExecutionSettings(response_format=ConsolidatedReport)

        # Set the chat history
        history = ChatHistory()
        history.add_system_message(system_message)
        history.add_user_message(user_message)

        # Get the response from the model
        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )

        return result.content
