"""This module implements a markdown report generator."""

import json


def json_to_markdown_report(json_file_name: str) -> str:
    """Generate a markdown report from a JSON file."""
    # Load the JSON data from the provided file
    with open(json_file_name, "r") as file:
        json_data = json.load(file)

    report = []

    # Add the title
    report.append(
        f"# {json_data['company_name']} \
Financial Health Analysis Report\n"
    )

    # Table of Contents
    report.append("## Table of Contents\n")
    report.append("1. [Financial Analysis](#financial-analysis)  \n")

    # Add each financial analysis as a sub-item in the TOC
    for i, analysis in enumerate(json_data["financial_analysis"], 1):
        report.append(
            f"   1.{i}. [{analysis['name']}]\
(#{analysis['name'].lower().replace(' ', '-')})  \n"
        )

    report.append("2. [News Analysis](#news-analysis)")
    report.append("3. [Conclusion](#conclusion)\n")

    # Financial Analysis
    report.append("## Financial Analysis\n")
    for analysis in json_data["financial_analysis"]:
        report.append(f"### {analysis['name']}\n")
        for metric in analysis["metrics"]:
            report.append(f"#### {metric['name']}\n")
            report.append(f"**Interpretation:** {metric['interpretation']}\n")
            # Create a table for the metric values
            report.append("| Date       | Value  | Unit  ")
            report.append("|------------|--------|-------")
            for value in metric["values"]:
                unit = value["unit"]
                if unit == "":
                    unit = "N/A"
                report.append(f"| {value['date']} | {value['value']} | {unit} |")
            report.append("\n")
        report.append(f"**Analysis:** {analysis['analysis']}\n\n")

    # News Analysis
    report.append("## News Analysis\n")

    # Bullish Indicators
    report.append("### Bullish Indicators\n")
    for bullish in json_data["news_analysis"]["bullish_indicators"]:
        report.append(f"#### {bullish['indicator']}\n")
        report.append("- " + "\n- ".join(bullish["items"]) + "\n")

    # Bearish Indicators
    report.append("### Bearish Indicators\n")
    for bearish in json_data["news_analysis"]["bearish_indicators"]:
        report.append(f"#### {bearish['indicator']}\n")
        report.append("- " + "\n- ".join(bearish["items"]) + "\n")

    # Mixed/Neutral Indicators
    report.append("### Mixed/Neutral Indicators\n")
    for mixed in json_data["news_analysis"]["mixed_neutral_indicators"]:
        report.append(f"#### {mixed['indicator']}\n")
        report.append("- " + "\n- ".join(mixed["items"]) + "\n")

    report.append(
        f"**News Analysis Summary:** \
{json_data['news_analysis']['analysis']}\n\n"
    )

    # Conclusion
    report.append("---")
    report.append("## Conclusion\n")
    report.append(f"{json_data['conclusion']}\n")

    # Return the formatted report as a single string
    return "\n".join(report)
