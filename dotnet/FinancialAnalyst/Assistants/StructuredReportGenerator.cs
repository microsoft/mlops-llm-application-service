namespace FinancialAnalyst.Assistants;

using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins;
using Microsoft.SemanticKernel.Services;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.ChatHistory;
using Microsoft.SemanticKernel.ExecutionSettings;

public class StructuredReportGenerator
{
    private readonly string aoaiToken;
    private readonly string aoaiBaseEndpoint;
    private readonly string llmDeploymentName;
    private readonly string aoaiApiVersion;

    public StructuredReportGenerator(string aoaiToken, string aoaiBaseEndpoint, string llmDeploymentName, string aoaiApiVersion)
    {
        this.aoaiToken = aoaiToken;
        this.aoaiBaseEndpoint = aoaiBaseEndpoint;
        this.llmDeploymentName = llmDeploymentName;
        this.aoaiApiVersion = aoaiApiVersion;
    }

    public async Task<string> GetConsolidatedReportAsync(string balanceSheetReport, string incomeReport, string cashFlowReport, string newsReport)
    {
        // Define system and user messages
        string systemMessage = @"
            You are a stock market financial analyst.

            You are specialized in analyzing the overall
            financial health of a company.

            For your analysis, you take into consideration:
            - the perspective of the individual analysis
            of the company's quarterly financial statements.
            - the financial news analysis related to the company.
            ";
        string userMessage = $@"
        Create an overall analysis report for the company,
        given the set of statement analysis, and financial news analysis below.

        Make sure to not repeat data from each given analysis
        and not to describe formulas in the report.

        Balance Sheet Statement Analysis:

        {balanceSheetReport}

        Income Statement Analysis:

        {incomeReport}

        Cash Flow Statement Analysis:

        {cashFlowReport}

        Financial News Analysis:

        {newsReport}
        ";

        // Initialize the kernel
        var kernel = new Kernel();

        // Add Azure OpenAI chat completion
        var chatCompletion = new AzureChatCompletion(
            deploymentName: llmDeploymentName,
            endpoint: aoaiBaseEndpoint,
            apiKey: aoaiToken,
            apiVersion: aoaiApiVersion
        );
        kernel.AddService(chatCompletion);

        // Set the logging level for semantic_kernel.kernel to DEBUG.
        SetupLogging();
        Logger.GetLogger("kernel").SetLevel(LogLevel.Debug);

        // Set structured output
        var executionSettings = new AzureChatPromptExecutionSettings(responseFormat: typeof(ConsolidatedReport));

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
