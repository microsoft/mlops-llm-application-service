"""
This module contains classes for implementing Pydantic data models.

The data models are used to define the structured data used when
creating the consolidated analysis report with the assistants.
"""

from typing import Annotated, List, Literal

from semantic_kernel.kernel_pydantic import KernelBaseModel


class BullishIndicator(KernelBaseModel):
    """A class representing a bullish indicator."""

    indicator: str
    items: List[str]


class BearishIndicator(KernelBaseModel):
    """A class representing a bearish indicator."""

    indicator: str
    items: List[str]


class MixedNeutralIndicator(KernelBaseModel):
    """A class representing a mixed/neutral indicator."""

    indicator: str
    items: List[str]


class NewsAnalysis(KernelBaseModel):
    """A class representing a news analysis."""

    bullish_indicators: List[BullishIndicator]
    bearish_indicators: List[BearishIndicator]
    mixed_neutral_indicators: List[MixedNeutralIndicator]
    analysis: str


class MetricValue(KernelBaseModel):
    """A class representing a metric value."""

    date: str
    value: float
    unit: Literal["USD", "%", "ratio"]


class Metric(KernelBaseModel):
    """A class representing a metric."""

    name: Literal[
        "current_ratio",
        "quick_ratio",
        "working_capital",
        "debt_to_equity_ratio",
        "gross_margin",
        "profit_margin",
        "operating_margin",
        "basic_earnings_per_share",
        "basic_price_to_earnings_ratio",
        "return_on_equity",
        "cash_flow_per_share",
        "free_cash_flow",
        "cash_flow_to_debt_ratio",
    ]
    interpretation: str
    values: List[MetricValue]


class FinancialAnalysis(KernelBaseModel):
    """A class representing a financial analysis."""

    name: Literal[
        "balance_sheet_statement_analysis",
        "income_statement_analysis",
        "cash_flow_statement_analysis",
    ]
    metrics: List[Metric]
    analysis: str


class ConsolidatedReport(KernelBaseModel):
    """A class representing a consolidated analysis report."""

    company_name: Annotated[
        str, "The name of the company, extracted from the financial statements."
    ]
    financial_analysis: List[FinancialAnalysis]
    news_analysis: NewsAnalysis
    conclusion: str
