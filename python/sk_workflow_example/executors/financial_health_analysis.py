from dotenv import load_dotenv
import asyncio
import os
import argparse

from assistants import assistants as assistants


async def main(stock_ticker, output_folder):
    load_dotenv(dotenv_path="./.env", override=True)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    news_analyst = assistants.NewsAnalyst()

    news_report = await news_analyst.get_news_report(stock_ticker=stock_ticker)
    print("NEWS REPORT\n-----------")
    print(news_report)
    print("==================================================================")

    # Save the news report to a file
    news_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_news_report.md"
    )
    with open(news_report_file, "w") as file:
        file.write(news_report)

    financial_analyst = assistants.FinancialAnalyst()

    report_type = "balance_sheet"
    balance_sheet_report_metrics = """
        current ratio,
        quick ratio,
        working capital,
        debt-to-equity ratio
    """
    balance_sheet_report = await financial_analyst.get_financial_report(
        stock_ticker=stock_ticker,
        report_type=report_type,
        report_metrics=balance_sheet_report_metrics
    )
    print("BALANCE SHEET REPORT\n--------------------")
    print(balance_sheet_report)
    print("==================================================================")

    # Save the balance sheet report to a file
    balance_sheet_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_balance_sheet_report.md"
    )
    with open(balance_sheet_report_file, "w") as file:
        file.write(balance_sheet_report)

    report_type = "income"
    income_report_metrics = """
        gross margin,
        profit margin,
        operating margin,
        earnings per share,
        price-to-earnings ratio,
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

    # Save the income report to a file
    income_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_income_report.md"
    )
    with open(income_report_file, "w") as file:
        file.write(income_report)

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

    # Save the cash flow report to a file
    cash_flow_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_cash_flow_report.md"
    )
    with open(cash_flow_report_file, "w") as file:
        file.write(cash_flow_report)

    report_generator = assistants.ReportGenerator()

    consolidated_report = await report_generator.get_consolidated_report(
        balance_sheet_report=balance_sheet_report,
        income_report=income_report,
        cash_flow_report=cash_flow_report,
        news_report=news_report
    )
    print("CONSOLIDATED REPORT\n-------------------")
    print(consolidated_report)
    print("==================================================================")

    # Save the consolidated report to a file
    consolidated_report_file = os.path.join(
        output_folder,
        f"{stock_ticker}_consolidated_report.md"
    )
    with open(consolidated_report_file, "w") as file:
        file.write(consolidated_report)

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
        default="../data/outputs",
        help="The folder where the output data will be saved."
    )
    args = parser.parse_args()
    asyncio.run(main(args.stock_ticker, args.output_folder))
