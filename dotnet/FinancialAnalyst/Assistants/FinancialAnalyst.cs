namespace FinancialAnalyst.Assistants;
using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins;
using Microsoft.SemanticKernel.Services;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.ChatHistory;
using Microsoft.SemanticKernel.ExecutionSettings;

public class FinancialAnalyst
{
    private readonly string aoaiToken;
    private readonly string aoaiBaseEndpoint;
    private readonly string llmDeploymentName;
    private readonly string secIdentity;

    public FinancialAnalyst(string aoaiToken, string aoaiBaseEndpoint, string llmDeploymentName, string secIdentity)
    {
        this.aoaiToken = aoaiToken;
        this.aoaiBaseEndpoint = aoaiBaseEndpoint;
        this.llmDeploymentName = llmDeploymentName;
        this.secIdentity = secIdentity;
    }

    public async Task<string> GetFinancialReportAsync(string stockTicker, string reportType, string reportMetrics)
    {
        // Define system and user messages
        string systemMessage = @"
        You are a stock market financial analyst.
        You are specialized in analyzing the financial health of a company,
        by using the financial statements of the company and computing
        financial metrics derived from the financial statements.
        ";
        string userMessage = $@"
        Analyze the financial health of {stockTicker} stock ticker, from the perspective of
        its financial statement of the type {reportType}.
        Calculate the following metrics,
        providing your interpretation of the results:

        {reportMetrics}

        **MAKE SURE** to calculate metrics for all date periods provided
        in the financial statement.

        When analyzing a financial statement of type 'cash_flow',
        you should also get the corresponding 'balance_sheet' statement,
        to be able to compute all asked metrics.

        When analyzing a financial statement of type 'income', you
        should also get the corresponding statement of type 'balance_sheet',
        to be able to compute all asked metrics,
        plus the latest stock price for the {stockTicker} stock ticker.
        ";

        // Initialize the kernel
        var kernel = new Kernel();

        // Add Azure OpenAI chat completion
        var chatCompletion = new AzureChatCompletion(
            deploymentName: llmDeploymentName,
            endpoint: aoaiBaseEndpoint,
            apiKey: aoaiToken
        );
        kernel.AddService(chatCompletion);

        // Set the logging level for semantic_kernel.kernel to DEBUG.
        SetupLogging();
        Logger.GetLogger("kernel").SetLevel(LogLevel.Debug);

        // Add the FinancialStatementsPlugin to the kernel
        var financialStatementsPlugin = new FinancialStatementsPlugin(secIdentity);
        kernel.AddPlugin(financialStatementsPlugin, "FinancialStatementsPlugin");

        // Add the StockPricePlugin to the kernel
        var stockPricePlugin = new StockPricePlugin();
        kernel.AddPlugin(stockPricePlugin, "StockPricePlugin");

        // Enable planning
        var executionSettings = new AzureChatPromptExecutionSettings(toolChoice: "auto")
        {
            FunctionChoiceBehavior = FunctionChoiceBehavior.Auto(autoInvoke: true, filters: new Dictionary<string, string>())
        };

        // Set the chat history
        var history = new ChatHistory();
        history.AddSystemMessage(systemMessage);
        history.AddUserMessage(userMessage);

        // Get the response from the model
        var result = await chatCompletion.GetChatMessageContentAsync(
            chatHistory: history,
            settings: executionSettings,
            kernel: kernel
        );

        return result.Content;
    }

    private void SetupLogging()
    {
        // Implement logging setup here
    }
}