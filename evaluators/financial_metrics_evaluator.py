import json
from typing import Any, Dict, List, Set


class FinancialMetricsEvaluator:
    """Evaluator for comparing financial metrics between ground truth and predictions."""

    def __init__(self, metrics_to_compare: List[str] = None):
        """
        Initialize the evaluator with optional specific metrics to compare.

        Args:
            metrics_to_compare: List of metric names to compare. If None, compares all metrics.
        """
        self.metrics_to_compare = metrics_to_compare or [
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

    def load_json(self, json_schema_path: str) -> Dict[str, Any]:
        """
        Load a JSON string into a dictionary.

        Args:
            json_string: JSON string to parse

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If JSON string is invalid
        """
        try:
            with open(json_schema_path, "r") as json_string:
                return json.load(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")

    def get_evaluation_dates(self, ground_truth: Dict[str, Any]) -> Set[str]:
        """
        Extract all evaluation dates from ground truth data.

        Args:
            ground_truth: Ground truth JSON dictionary

        Returns:
            Set of dates available for evaluation
        """
        return set(ground_truth.get("financial_metrics", {}).keys())

    def extract_predicted_metrics(self, predictions: Dict[str, Any], date: str) -> Dict[str, float]:
        """
        Extract metrics from the predictions JSON structure.

        Args:
            predictions: Predictions JSON dictionary
            date: Date to extract metrics for

        Returns:
            Dictionary of metric names to values
        """
        metrics = {}

        # Navigate through the financial analysis structure
        for analysis in predictions.get("financial_analysis", []):
            for metric in analysis.get("metrics", []):
                metric_name = metric["name"]
                if metric_name in self.metrics_to_compare:
                    for value in metric.get("values", []):
                        if value["date"] == date:
                            # Convert string values to float if needed
                            metric_value = value["value"]
                            if isinstance(metric_value, str):
                                try:
                                    metric_value = float(metric_value.replace(",", ""))
                                except ValueError:
                                    continue
                            metrics[metric_name] = metric_value

        return metrics

    def extract_ground_truth_metrics(self, ground_truth: Dict[str, Any], date: str) -> Dict[str, float]:
        """
        Extract metrics from the ground truth JSON structure.

        Args:
            ground_truth: Ground truth JSON dictionary
            date: Date to extract metrics for

        Returns:
            Dictionary of metric names to values
        """
        metrics = {}

        if date in ground_truth.get("financial_metrics", {}):
            date_metrics = ground_truth["financial_metrics"][date]

            # Navigate through different analysis types
            for analysis_type in ["balance_sheet_analysis", "income_statement_analysis", "cash_flow_analysis"]:
                if analysis_type in date_metrics:
                    for metric_name, value in date_metrics[analysis_type].items():
                        if metric_name in self.metrics_to_compare:
                            # Convert string values to float if needed
                            if isinstance(value, str):
                                try:
                                    value = float(value.replace(",", ""))
                                except ValueError:
                                    continue
                            metrics[metric_name] = value

        return metrics

    def calculate_accuracy(
        self, ground_truth_metrics: Dict[str, float], predicted_metrics: Dict[str, float], tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Calculate accuracy metrics between ground truth and predictions.

        Args:
            ground_truth_metrics: Dictionary of ground truth metrics
            predicted_metrics: Dictionary of predicted metrics
            tolerance: Acceptable difference ratio for considering values equal

        Returns:
            Dictionary containing accuracy metrics
        """
        total_metrics = len(self.metrics_to_compare)
        correct_predictions = 0
        compared_metrics = 0
        accuracy_details = {}

        for metric_name in self.metrics_to_compare:
            if metric_name in ground_truth_metrics and metric_name in predicted_metrics:
                compared_metrics += 1
                gt_value = ground_truth_metrics[metric_name]
                pred_value = predicted_metrics[metric_name]

                # Calculate relative difference
                if gt_value != 0:
                    relative_diff = abs(gt_value - pred_value) / abs(gt_value)
                    is_correct = relative_diff <= tolerance
                else:
                    is_correct = abs(pred_value) <= tolerance

                if is_correct:
                    correct_predictions += 1

                accuracy_details[metric_name] = {
                    "ground_truth": gt_value,
                    "prediction": pred_value,
                    "correct": is_correct,
                }

        accuracy = correct_predictions / compared_metrics if compared_metrics > 0 else 0

        return {
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_compared": compared_metrics,
            "missing_metrics": total_metrics - compared_metrics,
            "details": accuracy_details,
        }

    def evaluate_all_dates(self, ground_truth: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate predictions for all available dates in ground truth.

        Args:
            ground_truth: Ground truth JSON dictionary
            predictions: Predictions JSON dictionary

        Returns:
            Dictionary containing evaluation results for all dates
        """
        evaluation_dates = self.get_evaluation_dates(ground_truth)
        results = {}
        overall_correct = 0
        overall_total = 0

        for date in evaluation_dates:
            ground_truth_metrics = self.extract_ground_truth_metrics(ground_truth, date)
            predicted_metrics = self.extract_predicted_metrics(predictions, date)

            print(ground_truth_metrics)
            print(predicted_metrics)

            date_results = self.calculate_accuracy(ground_truth_metrics, predicted_metrics)
            results[date] = date_results

            overall_correct += date_results["correct_predictions"]
            overall_total += date_results["total_compared"]

        overall_accuracy = overall_correct / overall_total if overall_total > 0 else 0

        return {
            "overall_accuracy": overall_accuracy,
            "total_correct": overall_correct,
            "total_compared": overall_total,
            "results_by_date": results,
        }

    def __call__(self, *, ground_truth_json: str, predictions_json: str, **kwargs) -> Dict[str, Any]:
        """
        Evaluate financial metrics predictions against ground truth for all available dates.

        Args:
            ground_truth_json: Ground truth JSON string
            predictions_json: Predictions JSON string

        Returns:
            Dictionary containing evaluation results for all dates
        """
        try:
            ground_truth = self.load_json(ground_truth_json)
            predictions = self.load_json(predictions_json)

            return self.evaluate_all_dates(ground_truth, predictions)

        except ValueError as e:
            raise e
