namespace Models

public 
public record FinancialAnalysis(
    string Name,
    string[] Metrics,
    string Analysis
);

        name: Literal["balance_sheet_statement_analysis", "income_statement_analysis", "cash_flow_statement_analysis"]
    metrics: List[Metric]
    analysis: str