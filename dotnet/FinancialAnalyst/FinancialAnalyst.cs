
namespace FinancialAnalyst
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using FinancialAnalyst.Assistants;


public class FinancialHealthAnalysis
{
    private readonly string aoaiToken;
    private readonly string aoaiBaseEndpoint;
    private readonly string aoaiApiVersion;
    private readonly string bingSearchEndpoint;
    private readonly string bingSearchApiKey;
    private readonly string newsAnalystModel;
    private readonly string financialAnalystModel;
    private readonly int maxNews;
    private readonly string secIdentity;
    private readonly string structuredReportGeneratorModel;

    public FinancialHealthAnalysis(
        string aoaiToken,
        string aoaiBaseEndpoint,
        string aoaiApiVersion,
        string bingSearchEndpoint,
        string bingSearchApiKey,
        string newsAnalystModel,
        int maxNews,
        string financialAnalystModel,
        string secIdentity,
        string structuredReportGeneratorModel)
    {
        this.aoaiToken = aoaiToken;
        this.aoaiBaseEndpoint = aoaiBaseEndpoint;
        this.aoaiApiVersion = aoaiApiVersion;
        this.bingSearchEndpoint = bingSearchEndpoint;
        this.bingSearchApiKey = bingSearchApiKey;
        this.newsAnalystModel = newsAnalystModel;
        this.financialAnalystModel = financialAnalystModel;
        this.maxNews = maxNews;
        this.secIdentity = secIdentity;
        this.structuredReportGeneratorModel = structuredReportGeneratorModel;
    }

    public async Task<Dictionary<string, string>> GenerateReportAsync(string stockTicker)
    {
        var reports = new Dictionary<string, string>();

        // Create the news analyst assistant
        var newsAnalyst = new NewsAnalyst(
            aoaiToken: aoaiToken,
            aoaiBaseEndpoint: aoaiBaseEndpoint,
            llmDeploymentName: newsAnalystModel,
            bingSearchApiKey: bingSearchApiKey,
            bingSearchEndpoint: bingSearchEndpoint,
            maxNews: maxNews
        );

        // Get the news report for the stock ticker
        reports["news_report"] = await newsAnalyst.GetNewsReportAsync(stockTicker);

        Console.WriteLine($"news report: {reports["news_report"]}");

        // Create the financial analyst assistant
        var financialAnalyst = new FinancialAnalyst(
            aoaiToken: aoaiToken,
            aoaiBaseEndpoint: aoaiBaseEndpoint,
            llmDeploymentName: financialAnalystModel,
            secIdentity: secIdentity
        );

        // Get the financial reports for the stock ticker
        string reportType = "balance_sheet";
        string balanceSheetReportMetrics = @"
            current ratio,
            quick ratio,
            working capital,
            debt to equity ratio
        ";

        reports["balance_sheet_report"] = await financialAnalyst.GetFinancialReportAsync(
            stockTicker: stockTicker, reportType: reportType, reportMetrics: balanceSheetReportMetrics
        );

        reportType = "income";
        string incomeReportMetrics = @"
            gross margin,
            profit margin,
            operating margin,
            basic earnings per share,
            basic price to earnings ratio,
            return on equity
        ";
        reports["income_report"] = await financialAnalyst.GetFinancialReportAsync(
            stockTicker: stockTicker, reportType: reportType, reportMetrics: incomeReportMetrics
        );

        reportType = "cash_flow";
        string cashFlowReportMetrics = @"
            cash flow per share,
            free cash flow,
            cash flow to debt ratio
        ";
        reports["cash_flow_report"] = await financialAnalyst.GetFinancialReportAsync(
            stockTicker: stockTicker, reportType: reportType, reportMetrics: cashFlowReportMetrics
        );

        // Create the report generator assistant
        var structuredReportGenerator = new StructuredReportGenerator(
            aoaiToken: aoaiToken,
            aoaiBaseEndpoint: aoaiBaseEndpoint,
            llmDeploymentName: structuredReportGeneratorModel,
            aoaiApiVersion: aoaiApiVersion
        );

        // Generate the structured consolidated report
        reports["consolidated_report"] = await structuredReportGenerator.GetConsolidatedReportAsync(
            balanceSheetReport: reports["balance_sheet_report"],
            incomeReport: reports["income_report"],
            cashFlowReport: reports["cash_flow_report"],
            newsReport: reports["news_report"]
        );

        return reports;
    }
}