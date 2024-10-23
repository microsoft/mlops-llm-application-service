"""
This module contains classes for implementing Semantic Kernel plugins.

The plugins allow Semantic Kernel assistants configured with LLMs
to interact with external services and data sources.
"""

import os
import time
import requests
import nest_asyncio
from typing import Annotated, Literal
import edgar as edgar
import yfinance as yf

from semantic_kernel.functions import kernel_function


class NewsPlugin:
    """A class defining a plugin for fetching news articles."""

    @kernel_function(
        name="get_news",
        description="Get the latest news related to a stock ticker",
    )
    def get_news(
        self,
        ticker: Annotated[str, "The stock ticker for getting news"],
        retries: int = 3,
        delay: int = 2
    ) -> Annotated[str,
                   """News articles related to the stock ticker,
                   showing title, headline, and text"""]:
        """
        Get the latest news articles related to a stock ticker.

        Uses the Bing Search API.
        """
        # Add your Bing Search V7 subscription key
        # and endpoint to your environment variables.
        subscription_key = os.getenv("BING_SEARCH_API_KEY")
        endpoint = os.getenv("BING_SEARCH_ENDPOINT")

        # Query term(s) to search for
        q = f"most relevant financial news about {ticker}"

        # Construct a request
        mkt = "en-us"
        freshness = "month"
        count = 50
        safesearch = "Strict"
        sortby = "Relevance"
        params = {
            "q": q,
            "mkt": mkt,
            "freshness": freshness,
            "count": count,
            "safeSearch": safesearch,
            "sortBy": sortby
        }
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}

        search_results = ""

        # Retry loop
        for attempt in range(retries):
            # Call the API
            try:
                response = requests.get(
                    endpoint, headers=headers, params=params
                )
                response.raise_for_status()
                results = response.json()
                num_results = len(results["value"])

                for i in range(num_results):
                    name = results["value"][i]["name"]
                    # url = results["value"][i]["url"]
                    description = results["value"][i]["description"]

                    search_results += f"{name}\n{description}\n\n"

                # If successful, break out of the retry loop
                break
            except Exception as ex:
                if attempt < retries - 1:  # Check if more attempts are allowed
                    time.sleep(delay)  # Wait before retrying
                else:
                    search_results = f"""
                        Error fetching results after {retries} attempts:
                        {str(ex)}
                    """
                    return search_results

        return search_results


class FinancialStatementsPlugin:
    """A class defining a plugin for fetching financial statements."""

    @kernel_function(
        name="get_financial_statements",
        description="""
        Get the latest quarterly financial statements related to a stock ticker
        """,
    )
    def get_financial_statements(
        self,
        ticker: Annotated[
            str, "The stock ticker for getting financial statements"
        ],
        report_type: Annotated[
            Literal["balance_sheet", "income", "cash_flow"],
            """The type of financial statement to get.
            Valid values are 'balance_sheet', 'income', or 'cash_flow'"""
        ],
    ) -> Annotated[str, "Financial statement related to the stock ticker"]:
        """
        Get the latest quarterly financial statements for a stock ticker.

        Uses the edgar API to connect to the SEC database.
        """
        # Need to use nest_asyncio to run asyncio in edgar library,
        # when another event loop is already running
        nest_asyncio.apply()

        # Set SEC identity
        edgar.set_identity(os.getenv("SEC_IDENTITY"))

        # Get the latest quarterly financial reports for the stock ticker
        filings = edgar.Company(ticker).get_filings(form="10-Q").latest(1)
        ten_q = filings.obj()
        balance_sheet = ten_q.balance_sheet.to_dataframe().to_dict()
        income_stmt = ten_q.income_statement.to_dataframe().to_dict()
        cash_flow_stmt = ten_q.cash_flow_statement.to_dataframe().to_dict()

        # Return the financial report based on the report type
        if report_type == "balance_sheet":
            return balance_sheet
        elif report_type == "income":
            return income_stmt
        elif report_type == "cash_flow":
            return cash_flow_stmt
        else:
            return "Invalid report type"


class StockPricePlugin:
    """A class defining a plugin for fetching stock prices."""

    @kernel_function(
        name="get_stock_price",
        description="Get the latest stock price for a stock ticker",
    )
    def get_stock_price(
        self,
        ticker: Annotated[str, "The stock ticker for getting the stock price"]
    ) -> Annotated[str, "The latest stock price for the stock ticker"]:
        """
        Get the latest stock price for a stock ticker.

        Uses the Yahoo Finance API.
        """
        try:
            # Fetch the stock data for the last 1 day
            stock_data = yf.Ticker(ticker)
            # Get the history for the last 1 day
            stock_history = stock_data.history(period="1d")

            # Get the latest closing price
            latest_closing_price = round(
                float(stock_history.iloc[0]["Close"]), 2)

            return latest_closing_price

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            return None
