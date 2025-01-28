using System;
using System.Net.Http;
using System.Threading.Tasks;
using YahooFinanceApi;
using Microsoft.SemanticKernel;
namespace FinancialAnalyst.Plugins;

public class StockPricePlugin
{
    [KernelFunction("get_stock_price")]
    [Description("Get the stock price for a stock ticker")]
    public async Task<string> GetStockPriceAsync(
        [Description("The stock ticker for getting the stock price")] string ticker, 
        [Description(@"The income statemet date to use for the stock price.
            This corresponds to the period being analyzed.
            Format: 'YYYY-MM-DD')]" string statementDate)
    {
        try
        {
            // Fetch the stock data for the last 1 day
            var stockData = await Yahoo.Symbols(ticker).QueryAsync();
            var stockHistory = stockData[ticker].History;

            // Get the history for the specified date
            var historyForDate = stockHistory[DateTime.Parse(statementDate)];

            // Get the latest closing price
            var closingPrice = Math.Round((double)historyForDate.Close, 2);

            return closingPrice.ToString();
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error retrieving data for {ticker}: {e.Message}");
            return null;
        }
    }
}