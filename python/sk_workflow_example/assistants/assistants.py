import os, logging

from plugins import plugins as plugins

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

class NewsAnalyst:
    async def get_news_report(self, stock_ticker):
        # Define system and user messages
        system_message = f"""
        You are a stock market financial analyst.
        You are specialized in identifying and analyzing sentiment signals in financial news articles.
        """
        user_message = f"""
        You are given a list of news articles, most of them related to the {stock_ticker} stock ticker.
        You task is to analyze the news articles to determine whether they are bullish or bearish for the {stock_ticker} stock ticker. You can disregard the news articles that you think are not relevant for this analysis.
        Your response should be a rubrik regarding the overall sentiment of the news articles, as bullish, bearish, or mixed, and why you arrived at that conclusion.
        """

        # Initialize the kernel
        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=os.getenv("AOAI_GPT_DEPLOYMENT"),
            api_key=os.getenv("AOAI_API_KEY"),
            endpoint=os.getenv("AOAI_BASE_ENDPOINT")
        )
        kernel.add_service(chat_completion)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Add the NewsPlugin to the kernel
        kernel.add_plugin(
            plugins.NewsPlugin(),
            plugin_name="NewsPlugin")
        
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
    async def get_financial_report(self, stock_ticker, report_type, report_metrics):
        # Define system and user messages
        system_message = f"""
        You are a stock market financial analyst.
        You are specialized in analyzing the financial health of a company, by using the financial statements of the company and computing financial metrics derived from the financial statements.
        """
        user_message = f"""
        Analyze the financial health of {stock_ticker}, from the perspective of its financial statement of the type {report_type}.
        Calculate the following metrics, providing your interpretation of the results:
        {report_metrics}

        When analyzing a financial statement of type 'cash_flow', you should also get the corresponding statement of type 'balance_sheet', to be able to compute all asked metrics.

        When analyzing a financial statement of type 'income', you should also get the corresponding statement of type 'balance_sheet', to be able to compute all asked metrics, plus the latest stock price for the {stock_ticker} stock ticker.

        When calculating metrics, you should calculate them for all date periods provided in the financial statement.
        """

        # Initialize the kernel
        kernel = Kernel()

        # Add Azure OpenAI chat completion
        chat_completion = AzureChatCompletion(
            deployment_name=os.getenv("AOAI_GPT_DEPLOYMENT"),
            api_key=os.getenv("AOAI_API_KEY"),
            endpoint=os.getenv("AOAI_BASE_ENDPOINT")
        )
        kernel.add_service(chat_completion)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)

        # Add the FinancialStatementsPlugin to the kernel
        kernel.add_plugin(
            plugins.FinancialStatementsPlugin(),
            plugin_name="FinancialStatementsPlugin")
        
        # Add the StockPricePlugin to the kernel
        kernel.add_plugin(
            plugins.StockPricePlugin(),
            plugin_name="StockPricePlugin")
        
        # Enable planning
        execution_settings = AzureChatPromptExecutionSettings(tool_choice="auto")
        execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(auto_invoke=True, filters={})

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


class ReportGenerator:
    async def get_consolidated_report(self, balance_sheet_report, income_report, cash_flow_report, news_report):
        # Define system and user messages
        system_message = f"""
            You are a stock market financial analyst.
            You are specialized in analyzing the overall financial health of a company.
            For your analysis, you take into consideration:
            - the perspective of the individual analysis of the company's quarterly financial statements.
            - the financial news analysis related to the company.
            """
        user_message = f"""
        Create an overall analysis report for the company, given the set of statement analysis, and financial news analysis below.
        You should write the report in a markdown format, with a table of contents.
        Make sure to not repeat data from each given analysis or describe formulas in the report.

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
            deployment_name=os.getenv("AOAI_GPT_DEPLOYMENT"),
            api_key=os.getenv("AOAI_API_KEY"),
            endpoint=os.getenv("AOAI_BASE_ENDPOINT")
        )
        kernel.add_service(chat_completion)

        # Set the logging level for  semantic_kernel.kernel to DEBUG.
        setup_logging()
        logging.getLogger("kernel").setLevel(logging.DEBUG)
        
        # Enable planning
        execution_settings = AzureChatPromptExecutionSettings()

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
