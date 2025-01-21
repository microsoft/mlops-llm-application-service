import os
import argparse

from azure.ai.evaluation import evaluate, GroundednessEvaluator
from azure.ai.evaluation import AzureOpenAIModelConfiguration

from financial_metrics_evaluator import FinancialMetricsEvaluator


def main(financial_analisys_report: str, gt_report: str):

    aoai_token = os.environ.get("AOAI_TOKEN")
    aoai_base_endpoint = os.environ.get("AOAI_BASE_ENDPOINT")
    aoai_deployment = os.environ.get("AOAI_DEPLOYMENT")

    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=aoai_base_endpoint,
        api_key=aoai_token,
        azure_deployment=aoai_deployment,
    )

    groundedness_eval = GroundednessEvaluator(model_config=model_config)
    json_evaluator = FinancialMetricsEvaluator(gt_report)

    evaluators_config = {
        "json_evaluator": {
            "column_mapping": {
                "predictions_json_dict": "${data.financial_analysis}",
            }
        },
        "groundedness_eval": {
            "column_mapping": {
                "context": "${data.news_report}",
                "response": "${data.financial_analysis}",
            }
        },
    }

    results = evaluate(
        data=financial_analisys_report,
        evaluators={
            "json_evaluator": json_evaluator,
            "groundedness_eval": groundedness_eval,
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
