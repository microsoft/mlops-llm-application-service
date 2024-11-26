"""
This script runs on Azure ML as a parallel run step.

It processes a single batch of stock tickers.
"""

import argparse
import datetime
import json
import os
import sys

from sk_financial_analyst.executors.batch_executor import process_batch_sync


def init():
    """Initialize the script."""
    global args

    args = parse_args()
    print(f"Initialized parallel_step.py with args: {args}")


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Batch financial health analysis with\
              AML parallel run and asyncio."
    )
    parser.add_argument("--batch_output_file", type=str, required=True, help="File name for the output JSONL file.")
    parser.add_argument("--output_folder", type=str, required=True, help="Folder for output files.")
    parser.add_argument("--logging_enabled", action="store_true", default=False, help="Enable logging.")
    parser.add_argument(
        "--in_batch_concurrency", type=int, required=True, help="Maximum number of concurrent tasks within each batch."
    )
    parser.add_argument(
        "--input_key", type=str, required=True, help="The key in the JSONL file that contains the stock ticker symbol."
    )
    parser.add_argument("--retries", type=int, required=True, help="Number of retry attempts for failed processes.")

    args, _ = parser.parse_known_args()
    return args


def run(mini_batch):
    """
    Process a single batch of stock tickers.

    Args:
        mini_batch (list): List of input files.

    Returns:
        list: List of processed results.
    """
    print(f"Started run() in parallel_step.py: {datetime.datetime.now().isoformat()}")
    for input_file in mini_batch:
        # Load tickers from JSONL input file
        try:
            with open(input_file, "r") as f:
                lines = [json.loads(line) for line in f]
        except FileNotFoundError:
            print(f"Input file {input_file} not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from input file: {e}")
            sys.exit(1)

        tickers = [line[args.input_key] for line in lines if args.input_key in line]
        print(f"Tickers: {tickers}")

        if not tickers:
            print(f"No tickers found with key '{args.input_key}' in the input file.")
            sys.exit(1)

        # Get batch_number from the input_file name
        batch_number = int(input_file.split("_")[-1].split(".")[0])

        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(script_dir, "../../config/config.yaml")
        try:
            batch_results = process_batch_sync(
                config_file, batch_number, tickers, args.retries, args.in_batch_concurrency, args.logging_enabled
            )
            if batch_results:
                batch_output_path = os.path.join(args.output_folder, str(batch_number) + "_" + args.batch_output_file)
                # Remove contents from the output file if exists
                # to prevent appending to old data
                try:
                    if os.path.exists(batch_output_path):
                        os.remove(batch_output_path)
                except IOError as e:
                    print(
                        f"""Error removing existing output file
                        {batch_output_path}: {e}
                        """
                    )
                # Append successful results to the output file
                try:
                    with open(batch_output_path, "a") as f:
                        for item in batch_results:
                            f.write(json.dumps(item) + "\n")
                except IOError as e:
                    print(
                        f"""Error writing to output file
                        {batch_output_path}: {e}
                        """
                    )
        except Exception as e:
            print(f"An error occurred while processing a batch: {e}")
            # Optionally, handle or log the error as needed
        print(f"Batch results: {batch_results}")
    print(f"Finished run() in parallel_step.py: {datetime.datetime.now().isoformat()}")
    return batch_results
