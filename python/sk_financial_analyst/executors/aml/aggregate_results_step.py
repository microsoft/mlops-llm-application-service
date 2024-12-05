"""
This script runs on Azure ML as a Python command step.

It aggregates multiple JSONL files into a single JSONL file.
"""

import argparse
import json
import os


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Aggregate JSONL files into a single file.")
    parser.add_argument("--input_folder", type=str, required=True, help="Input folder containing JSONL files.")
    parser.add_argument("--output_file", type=str, required=True, help="Output JSONL file path.")
    return parser.parse_args()


def aggregate_jsonl_files(input_folder, output_file):
    """
    Aggregate multiple JSONL files into a single JSONL file.

    Args:
        input_folder (str): Path to the folder containing JSONL files.
        output_file (str): Path to the output JSONL file.
    """
    aggregated_results = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".jsonl"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    for line in f:
                        try:
                            aggregated_results.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            print(f"Skipping invalid line in {file_path}: {e}")

    with open(output_file, "w") as out_file:
        for item in aggregated_results:
            out_file.write(json.dumps(item) + "\n")


def main():
    """Aaggregate JSONL files."""
    args = parse_args()
    aggregate_jsonl_files(args.input_folder, args.output_file)


if __name__ == "__main__":
    main()
