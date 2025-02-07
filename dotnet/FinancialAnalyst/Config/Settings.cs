namespace FinancialAnalyst.config;

public class FinanacialAnalystSettings
{

#pragma warning disable CA1056
    // Reading the configuration.
    public string Uri { get; set; }
#pragma warning restore CA1056

    public string ModelDeploymentName { get; set; }

    public string CompletionsDeploymentStandard { get; set; }


}