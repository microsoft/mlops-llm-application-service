using Utilities.Config;
using Utilities.Plugins;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using Microsoft.SemanticKernel.Plugins.Web;
using Microsoft.SemanticKernel.Plugins.Web.Bing;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins;
using Microsoft.SemanticKernel.Services;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.ChatHistory;
using Microsoft.SemanticKernel.ExecutionSettings;
namespace FinancialAnalyst.Assistants;


public class NewsAnalyst
{

    private readonly Kernel _kernel;
    private AzureOpenAI _openAiSettings;

    privare string _system_message = @"
        You are a stock market financial analyst.
        You are specialized in identifying and analyzing sentiment signals
        in financial news articles.
        ";
    privare string _user_message = @"
        You are given a list of news articles,
        most of them related to the {stock_ticker} stock ticker.
        You task is to analyze the news articles to determine whether
        they are bullish or bearish for the {stock_ticker} stock ticker.
        You can disregard the news articles that you think are not relevant
        for this analysis.
        Your response should be a rubrik regarding the overall sentiment
        of the news articles, as bullish, bearish, or mixed,
        and why you arrived at that conclusion.";

    public NewsAnalyst()
    {

        var builder = Kernel.CreateBuilder()
                        .AddAzureOpenAIChatCompletion(modelId: "",
                        apiKey: '');
        _kernel = builder.Build();
        _kernel.ImportPluginFromObject(_kernel.Plugin);
                        

    }

    public async Task<string> GetNewsReport(string stockTicker)
    {

        // Define system and user messages
        string systemMessage = @"
        You are a stock market financial analyst.
        You are specialized in identifying and analyzing sentiment signals
        in financial news articles.
        ";

        string userMessage = $@"
        You are given a list of news articles,
        most of them related to the {stockTicker} stock ticker.
        Your task is to analyze the news articles to determine whether
        they are bullish or bearish for the {stockTicker} stock ticker.
        You can disregard the news articles that you think are not relevant
        for this analysis.
        Your response should be a rubric regarding the overall sentiment
        of the news articles, as bullish, bearish, or mixed,
        and why you arrived at that conclusion.
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

        // Add the NewsPlugin to the kernel
        var newsPlugin = new NewsPlugin(
            bingSearchApiKey: bingSearchApiKey,
            bingSearchEndpoint: bingSearchEndpoint,
            maxNews: maxNews
        );
        kernel.AddPlugin(newsPlugin, "NewsPlugin");

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
        while (history.Messages.Count < 4)
        {
            var result = await chatCompletion.GetChatMessageContentAsync(
                chatHistory: history,
                settings: executionSettings,
                kernel: kernel
            );

            history.AddAssistantMessage(result.Content);
        }

        return history.Messages.Last().Content;


     }
    
}
    