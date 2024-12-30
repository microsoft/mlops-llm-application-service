"""Evaluation module providing utilities for financial analysis comparisons."""

import argparse
from azure.ai.evaluation import evaluate
from evaluators.financial_metrics_evaluator import FinancialMetricsEvaluator


def main(financial_analisys_report: str, gt_report: str):
    """Run the main evaluation for financial metrics.

    Args:
        financial_analisys_report (str): Path to or content of the financial analysis report.
        gt_report (str): Path to or content of the ground truth report.
    """
    json_evaluator = FinancialMetricsEvaluator(gt_report)

    evaluators_config = {
        "json_evaluator": {
            "column_mapping": {
                "predictions_json_dict": "${data.financial_analysis}",
            }
        }
    }

    results = evaluate(
        data=financial_analisys_report,
        evaluators={
            "json_evaluator": json_evaluator,
        },
        evaluator_config=evaluators_config,
        # Optionally provide your AI Studio project information to track your evaluation results in your Azure AI Studio project
        # azure_ai_project = azure_ai_project,
        output_path="./evalresults.json",
    )

    print(results["studio_url"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser("evaluation_parameters")
    parser.add_argument(
        "--gt_report",
        type=str,
        required=True,
        help="Path to the file containing ground truth data",
    )
    parser.add_argument(
        "--financial_analisys_report",
        type=str,
        required=False,
        help="Path to the file containing reposrt created by financial analyst",
    )

    args = parser.parse_args()

    main(args.financial_analisys_report, args.gt_report)
