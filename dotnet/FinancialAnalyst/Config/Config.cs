using System.Globalization;
using Microsoft.Extensions.Configuration;

namespace FinancialAnalyst.Config;

public static class Config
{
	private static IConfigurationRoot _config = new ConfigurationBuilder()
							.AddJsonFile("appsettings.json")
							.Build();

	public static string AzureTenantId
	{
		get => _config.GetSection("AZURE_TENANT_ID").Value ??
						throw new InvalidOperationException("AZURE_TENANT_ID is not set");
	}

	public static string AzureClientId
	{
		get => _config.GetSection("AZURE_CLIENT_ID").Value ??
						throw new InvalidOperationException("AZURE_CLIENT_ID is not set");
	}

	public static string AzureClientSecret
	{
		get => _config.GetSection("AZURE_CLIENT_SECRET").Value ??
						throw new InvalidOperationException("AZURE_CLIENT_SECRET is not set");
	}

	public static string AoaiEmbeddingDeploymentId
	{
		get => _config.GetSection("AOAI_EMBEDDING_DEPLOYMENT_ID").Value ??
						throw new InvalidOperationException("AOAI_EMBEDDING_DEPLOYMENT_ID is not set");
	}

	public static string AoaiLLMDeploymentId
	{
		get => _config.GetSection("AOAI_LLM_DEPLOYMENT_ID").Value ??
						throw new InvalidOperationException("AOAI_LLM_DEPLOYMENT_ID is not set");
	}

	public static string AoaiEndpoint
	{
		get => _config.GetSection("AOAI_ENDPOINT").Value ??
						throw new InvalidOperationException("AOAI_ENDPOINT is not set");
	}

	public static string AoaiApiKey
	{
		get => _config.GetSection("AOAI_API_KEY").Value ??
						throw new InvalidOperationException("AOAI_API_KEY is not set");
	}

	public static string Author
	{
		get => _config.GetSection("AUTHOR").Value ??
						throw new InvalidOperationException("AUTHOR is not set");
	}

	public static string Region
	{
		get => _config.GetSection("REGION").Value ??
						throw new InvalidOperationException("REGION is not set");
	}

	public static string SubscriptionId
	{
		get => _config.GetSection("SUBSCRIPTION_ID").Value ??
						throw new InvalidOperationException("SUBSCRIPTION_ID is not set");
	}

	public static string ResourceGroupName
	{
		get => _config.GetSection("RESOURCE_GROUP_NAME").Value ??
						throw new InvalidOperationException("RESOURCE_GROUP_NAME is not set");
	}

	public static string WorkspaceName
	{
		get => _config.GetSection("WORKSPACE_NAME").Value ??
						throw new InvalidOperationException("WORKSPACE_NAME is not set");
	}

	public static int TestCaseRepetitions
	{
		get => int.Parse(_config.GetSection("TEST_CASE_REPETITIONS").Value ?? "2", CultureInfo.CurrentCulture);
	}

	public static double LlmTemperature
	{
		get => double.Parse(_config.GetSection("LLM_TEMPERATURE").Value ?? "0.2", CultureInfo.CurrentCulture);
	}

	public static double LlmTopP
	{
		get => double.Parse(_config.GetSection("LLM_TOP_P").Value ?? "0.1", CultureInfo.CurrentCulture);
	}

#pragma warning disable CA1819 // Properties should not return arrays
	public static string[] EnabledTestCaseCategories
#pragma warning restore CA1819 // Properties should not return arrays
	{
		get => _config.GetSection("ENABLED_TEST_CASE_CATEGORIES").Value?
																 .Split("|")
																 .Select(s => s.Trim())
																 .ToArray() ?? [];
	}
}
