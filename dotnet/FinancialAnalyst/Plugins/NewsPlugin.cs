namespace FinancialAnalyst.Plugins

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using Microsoft.SemanticKernel;

public class NewsPlugin
{
    private readonly string _bingSearchApiKey = '';
    private readonly string _bingSearchEndpoint = '';
    private reaonly maxNews = 10;

    public NewsPlugin(LoggerFactory loggerFactory)
    {}

    [KernelFunction("get_news")]
    [Description("Get the latest news related to a stock ticker")]
    public async Task<string> GetNews(
         [Description("The stock ticker for getting news")]string ticker,
         int retries = 3,
         int delay = 2
        )
    {
        string endpoint = _bingSearchEndpoint;
        string query = $"most relevant financial news about {ticker}";
        string market = "en-us";
        string freshness = "month";
        string safeSearch = "Strict";
        string sortBy = "Relevance";
        int count = maxNews;
        var parameters = new Dictionary<string, string>
        {
            { "q", query },
            { "mkt", market },
            { "freshness", freshness },
            { "count", count.ToString() },
            { "safeSearch", safeSearch },
            { "sortBy", sortBy }
        };

        var headers = new Dictionary<string, string>
        {
            { "Ocp-Apim-Subscription-Key", bingSearchApiKey }
        };
        string searchResults = "";
        using (HttpClient client = new HttpClient())
        {
            for (int attempt = 0; attempt < retries;  attempt++) {
                try
                {
                    var requestUri = new Uri(QueryHelpers.AddQueryString(_bingSearchEndpoint, parameters));
                    var request = new HttpRequestMessage(HttpMethod.Get, requestUri);

                    foreach (var header in headers)
                    {
                        request.Headers.Add(header.Key, header.Value);
                    }

                    HttpResponseMessage response = await client.SendAsync(request);
                    response.EnsureSuccessStatusCode();

                    string jsonResponse = await response.Content.ReadAsStringAsync();
                    JObject results = JObject.Parse(jsonResponse);
                    int numResults = results["value"].Count();

                    for (int i = 0; i < numResults; i++)
                    {
                        string name = results["value"][i]["name"].ToString();
                        string description = results["value"][i]["description"].ToString();

                        searchResults += $"{name}\n{description}\n\n";
                    }

                    break; // If successful, break out of the retry loop
                }
                catch (Exception ex)
                {
                    if (attempt < retries - 1)
                    {
                        await Task.Delay(delay); // Wait before retrying
                    }
                    else
                    {
                        searchResults = $"Error fetching results after {retries} attempts:\n{ex.Message}";
                        return searchResults;
                    }
                }
            }
        }

        return searchResults;
    }
          
}