using System;
using System.Net.Http;
using System.Threading.Tasks;
using YahooFinanceApi;
using Microsoft.SemanticKernel;
namespace FinancialAnalyst.Plugins;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Edgar;
using Newtonsoft.Json;

public class FinancialStatementPlugin
{
    private readonly string secIdentity = "";

    [KernelFunction("get_financial_statements")]
    [Description("Get the stock price for a stock ticker")]
    public async Task<string> GetStockPriceAsync(
        [Description("The stock ticker for getting the stock price")] string ticker,
        [Description(@"The income statemet date to use for the stock price.
            This corresponds to the period being analyzed.
            Format: 'YYYY-MM-DD')]" string statementDate)
    {
        try
        {
            // Set SEC identity
            EdgarClient.SetIdentity(secIdentity);

            // Get the latest quarterly financial reports for the stock ticker
            var filings = await EdgarClient.GetCompanyFilingsAsync(ticker, "10-Q", 1);
            var tenQ = filings;

            var balanceSheet = JsonConvert.SerializeObject(tenQ.BalanceSheet.ToDictionary());
            var balanceSheetPeriods = JsonConvert.SerializeObject(tenQ.BalanceSheet.Periods);
            var incomeStatement = JsonConvert.SerializeObject(tenQ.IncomeStatement.ToDictionary());
            var incomeStatementPeriods = JsonConvert.SerializeObject(tenQ.IncomeStatement.Periods);
            var cashFlowStatement = JsonConvert.SerializeObject(tenQ.CashFlowStatement.ToDictionary());
            var cashFlowStatementPeriods = JsonConvert.SerializeObject(tenQ.CashFlowStatement.Periods);

            // Return the financial report based on the report type
            switch (reportType)
            {
                case "balance_sheet":
                    return $"Balance Sheet Periods: {balanceSheetPeriods}\n{balanceSheet}";
                case "income":
                    return $"Income Statement Periods: {incomeStatementPeriods}\n{incomeStatement}";
                case "cash_flow":
                    return $"Cash Flow Statement Periods: {cashFlowStatementPeriods}\n{cashFlowStatement}";
                default:
                    return "Invalid report type";
            }
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error retrieving data for {ticker}: {e.Message}");
            return null;
        }
    }

}