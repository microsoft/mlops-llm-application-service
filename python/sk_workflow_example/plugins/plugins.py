import os, requests, nest_asyncio, time
from typing import Annotated, Literal
import edgar as edgar
import yfinance as yf

from semantic_kernel.functions import kernel_function


class NewsPlugin:
    @kernel_function(
        name="get_news",
        description="Get the latest news related to a stock ticker",
    )
    def get_news(self, ticker: Annotated[str, "The stock ticker for getting news"], retries: int = 3, delay: int = 2) -> Annotated[str, "News articles related to the stock ticker, showing title, headline, and text"]:
        # Add your Bing Search V7 subscription key and endpoint to your environment variables.
        subscription_key = os.getenv("BING_SEARCH_API_KEY")
        endpoint = os.getenv("BING_SEARCH_ENDPOINT")

        # Query term(s) to search for. 
        q = f"most relevant financial news about {ticker}"

        # Construct a request
        mkt = "en-us"
        freshness = "month"
        count = 50
        safeSearch = "Strict"
        sortBy = "Relevance"
        params = { "q": q, "mkt": mkt, "freshness": freshness, "count": count, "safeSearch": safeSearch, "sortBy": sortBy }
        headers = { "Ocp-Apim-Subscription-Key": subscription_key }

        search_results = ""

        # Retry loop
        for attempt in range(retries):
            # Call the API
            try:
                response = requests.get(endpoint, headers=headers, params=params)
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

                    # # Make a GET request to fetch the raw HTML content
                    # try:
                    #     response = requests.get(url)
                    #     if response.status_code == 200:
                    #         # Parse the content with BeautifulSoup
                    #         soup = BeautifulSoup(response.content, "html.parser")
                    #         # Extract textual content
                    #         text = soup.get_text(separator=" ", strip=True)
                    #         # Limit the length of the content to 5000 characters
                    #         text = text[:5000]
                    #     else:
                    #         text = f"Failed to fetch content, status code: {response.status_code}"

                    #     # search_results.append({"title": name, "url": url, "headline": description, "text": text})
                    #     # search_results += f"Title: {name}\nURL: {url}\nHeadline: {description}\nText: {text}\n\n"
                    #     search_results += f"{name}\n{description}\n{text}\n\n"
                    # except Exception as ex:
                    #     # search_results.append({"title": name, "url": url, "headline": description, "text": f"Error fetching content: {str(ex)}"})
                    #     # search_results += f"Title: {name}\nURL: {url}\nHeadline: {description}\nText: Error fetching content: {str(ex)}\n\n"
                    #     search_results += f"{name}\n{description}\nError fetching content: {str(ex)}\n\n"

            except Exception as ex:
                if attempt < retries - 1:  # Check if more attempts are allowed
                    time.sleep(delay)  # Wait before retrying
                else:
                    search_results = f"Error fetching results after {retries} attempts: {str(ex)}"
                    return search_results
        
        return search_results


class FinancialStatementsPlugin:
    @kernel_function(
        name="get_financial_statements",
        description="Get the latest quarterly financial statements related to a stock ticker",
    )
    def get_financial_statements(
        self,
        ticker: Annotated[str, "The stock ticker for getting financial statements"],
        report_type: Annotated[Literal["balance_sheet", "income", "cash_flow"], "The type of financial statement to get. Valid values are 'balance_sheet', 'income', or 'cash_flow'"],
        ) -> Annotated[str, "Financial statement related to the stock ticker"]:

        # Need to use nest_asyncio to run asyncio in edgar library, when another event loop is already running
        nest_asyncio.apply()

        # Set SEC identity
        edgar.set_identity(os.getenv("SEC_IDENTITY"))

        # Get the latest quarterly financial reports for the stock ticker
        filings = edgar.Company(ticker).get_filings(form="10-Q").latest(1)
        ten_q = filings.obj()
        balance_sheet = ten_q.balance_sheet.to_dataframe().to_dict()
        income_statement = ten_q.income_statement.to_dataframe().to_dict()
        cash_flow_statement = ten_q.cash_flow_statement.to_dataframe().to_dict()

        # Return the financial report based on the report type
        if report_type == "balance_sheet":
            return balance_sheet
        elif report_type == "income":
            return income_statement
        elif report_type == "cash_flow":
            return cash_flow_statement
        else:
            return "Invalid report type"


class StockPricePlugin:
    @kernel_function(
        name="get_stock_price",
        description="Get the latest stock price for a stock ticker",
    )
    def get_stock_price(self, ticker: Annotated[str, "The stock ticker for getting the stock price"]) -> Annotated[str, "The latest stock price for the stock ticker"]:
        try:
            # Fetch the stock data for the last 1 day
            stock_data = yf.Ticker(ticker)
            # Get the history for the last 1 day
            stock_history = stock_data.history(period="1d")
            
            # Get the latest closing price
            latest_closing_price = round(float(stock_history.iloc[0]["Close"]), 2)
            
            return latest_closing_price

        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
            return None
