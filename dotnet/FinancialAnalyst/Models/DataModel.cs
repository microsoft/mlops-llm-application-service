using System;
using System.Collections.Generic;

namespace Models
{
    public class KernelBaseModel
    {
        // Base model implementation
    }

    public class BullishIndicator : KernelBaseModel
    {
        public string Indicator { get; set; }
        public List<string> Items { get; set; }
    }

    public class BearishIndicator : KernelBaseModel
    {
        public string Indicator { get; set; }
        public List<string> Items { get; set; }
    }

    public class MixedNeutralIndicator : KernelBaseModel
    {
        public string Indicator { get; set; }
        public List<string> Items { get; set; }
    }

    public class NewsAnalysis : KernelBaseModel
    {
        public List<BullishIndicator> BullishIndicators { get; set; }
        public List<BearishIndicator> BearishIndicators { get; set; }
        public List<MixedNeutralIndicator> MixedNeutralIndicators { get; set; }
        public string Analysis { get; set; }
    }

    public class MetricValue : KernelBaseModel
    {
        public string Date { get; set; }
        public float Value { get; set; }
        public string Unit { get; set; } // "USD", "%", "ratio"
    }

    public class Metric : KernelBaseModel
    {
        public string Name { get; set; } // "current_ratio", "quick_ratio", etc.
        public string Interpretation { get; set; }
        public List<MetricValue> Values { get; set; }
    }

    public class FinancialAnalysis : KernelBaseModel
    {
        public string Name { get; set; } // "balance_sheet_statement_analysis", etc.
        public List<Metric> Metrics { get; set; }
        public string Analysis { get; set; }
    }

    public class ConsolidatedReport : KernelBaseModel
    {
        public string CompanyName { get; set; }
        public List<FinancialAnalysis> FinancialAnalysis { get; set; }
        public NewsAnalysis NewsAnalysis { get; set; }
        public string Conclusion { get; set; }
    }
}