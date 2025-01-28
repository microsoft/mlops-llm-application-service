import json
from typing import Any, Dict


class FinancialMetricsEvaluator:
    """An evaluator for comparing financial metrics between actual and predicted values."""

    def __init__(self, ground_truth_json: str):
        """Initialize with ground truth data file."""
        with open(ground_truth_json, "r") as f:
            self.ground_truth = json.load(f)

        # List of financial metrics we want to compare
        self.metrics_to_compare = [
            "current_ratio",
            "quick_ratio",
            "working_capital",
            "debt_to_equity_ratio",
            "gross_margin",
            "profit_margin",
            "operating_margin",
            "return_on_equity",
            "cash_flow_to_debt_ratio",
            "free_cash_flow",
        ]

    def get_ground_truth_values(self, date: str) -> Dict[str, float]:
        """Get ground truth values for a specific date."""
        metrics = {}
        date_data = self.ground_truth.get("financial_metrics", {}).get(date, {})

        # Flatten the structure - look for metrics in all analysis types
        for analysis in ["balance_sheet_analysis", "income_statement_analysis", "cash_flow_analysis"]:
            if analysis in date_data:
                for metric, value in date_data[analysis].items():
                    if metric in self.metrics_to_compare:
                        # Convert string values to float
                        if isinstance(value, str):
                            value = float(value.replace(",", ""))
                        metrics[metric] = value

        return metrics

    def get_predicted_values(self, predictions: list, date: str) -> Dict[str, float]:
        """Get predicted values for a specific date."""
        metrics = {}

        for analysis in predictions:
            for metric in analysis.get("metrics", []):
                name = metric["name"]
                if name in self.metrics_to_compare:
                    for value in metric.get("values", []):
                        if value["date"] == date:
                            val = value["value"]
                            if isinstance(val, str):
                                val = float(val.replace(",", ""))
                            metrics[name] = val

        return metrics

    def compare_values(
        self, actual: Dict[str, float], predicted: Dict[str, float], tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """Compare actual and predicted values within a tolerance."""
        correct = 0
        compared = 0
        details = {}

        for metric in self.metrics_to_compare:
            if metric in actual and metric in predicted:
                compared += 1
                actual_val = actual[metric]
                pred_val = predicted[metric]

                # Simple relative difference check
                is_correct = abs(actual_val - pred_val) <= abs(actual_val * tolerance)
                if is_correct:
                    correct += 1

                details[metric] = {"ground_truth": actual_val, "prediction": pred_val, "correct": is_correct}

        return {
            "accuracy": correct / compared if compared > 0 else 0,
            "correct_predictions": correct,
            "total_compared": compared,
            "details": details,
        }

    def evaluate_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all predictions against ground truth."""
        dates = self.ground_truth.get("financial_metrics", {}).keys()
        total_correct = 0
        total_compared = 0
        results = {}

        for date in dates:
            actual = self.get_ground_truth_values(date)
            predicted = self.get_predicted_values(predictions, date)
            date_results = self.compare_values(actual, predicted)

            results[date] = date_results
            total_correct += date_results["correct_predictions"]
            total_compared += date_results["total_compared"]

        return {
            "overall_accuracy": total_correct / total_compared if total_compared > 0 else 0,
            "total_correct": total_correct,
            "total_compared": total_compared,
            "results_by_date": results,
        }

    def __call__(self, predictions_json_dict: str, **kwargs):
        """
        Evaluate financial metrics predictions against ground truth for all available dates.

        Args:
            predictions_json_dict: Predictions json dict

        Returns:
            Dictionary containing evaluation results for all dates
        """
        return self.evaluate_predictions(predictions_json_dict)
