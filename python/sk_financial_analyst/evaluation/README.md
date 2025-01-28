# Evaluation Script README

This README provides instructions on how to run the `eval.py` script located in the `sk_financial_analyst/evaluation` directory.

## Running the Evaluation Script

To run the `eval.py` script, use the following command:
```sh
python eval.py -h
```

## Example

Here is an example of running the `eval.py` script with a specific configuration:
```sh
python evaluation/eval.py --gt_report ./data/gt_data/MSFT_financial_dates_ground_truth_20241106.json  --financial_analisys_report ./data/outputs/MSFT_consolidated_report_combined.jsonl
```
