"""
This module contains classes for implementing Pydantic data models.

The data models are used to define the structured data used when
creating the consolidated analysis report with the assistants.
"""

from semantic_kernel.kernel_pydantic import KernelBaseModel

from typing import List


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
    unit: str


class Metric(KernelBaseModel):
    """A class representing a metric."""

    name: str
    interpretation: str
    values: List[MetricValue]


class FinancialAnalysis(KernelBaseModel):
    """A class representing a financial analysis."""

    name: str
    metrics: List[Metric]
    analysis: str


class ConsolidatedReport(KernelBaseModel):
    """A class representing a consolidated analysis report."""

    company_name: str
    financial_analysis: List[FinancialAnalysis]
    news_analysis: NewsAnalysis
    conclusion: str
