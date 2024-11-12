"""
This script generates financial health analysis of companies.

It processes multiple batches in parallel.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor

from sk_financial_analyst.executors.single_item_executor import generate_report


def process_batch_sync(batch_number, batch, retries, in_batch_concurrency, logging_enabled):
    """
    Process a single batch of tickers.

    Synchronous wrap function using asyncio for concurrency within the batch.

    Args:
        batch_number (int): The current batch number.
        batch (list): List of stock tickers in the current batch.
        retries (int): Number of retry attempts for failed processes.
        concurrency_limit (int): Maximum number of concurrent \
            tasks within the batch.

    Returns:
        list: List of successful report dictionaries.
    """
    if not logging_enabled:
        logging.disable(sys.maxsize)

    async def process_ticker(ticker):
        """
        Generate a financial health report for a single ticker with retries.

        Asynchronous function.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            dict or None: The generated report dictionary if successful, \
                else None.
        """
        for attempt in range(1, retries + 1):
            print(
                f"""
                [Batch {batch_number}] Generating financial health analysis
                for {ticker} (Attempt {attempt})...
                """
            )
            try:
                report_results = await generate_report(ticker)
                print(
                    f"""
                    [Batch {batch_number}] Financial health analysis
                    for {ticker} generated.
                    """
                )
                return {
                    "ticker": ticker,
                    "consolidated_report": report_results.get("consolidated_report"),
                    "news_report": report_results.get("news_report"),
                    "balance_sheet_report": report_results.get("balance_sheet_report"),
                    "income_report": report_results.get("income_report"),
                    "cash_flow_report": report_results.get("cash_flow_report"),
                }
            except Exception as e:
                print(
                    f"""
                    [Batch {batch_number}] Error processing {ticker}
                    on attempt {attempt}: {e}
                    """
                )
                if attempt < retries:
                    await asyncio.sleep(3)  # Wait before retrying
        return None

    async def run_batch():
        """
        Process all tickers in the batch concurrently.

        Uses a semaphore for limiting concurrency.

        Returns:
            list: List of successful reports.
        """
        semaphore = asyncio.Semaphore(in_batch_concurrency)

        async def sem_process(ticker):
            async with semaphore:
                return await process_ticker(ticker)

        tasks = [asyncio.create_task(sem_process(ticker)) for ticker in batch]
        results = await asyncio.gather(*tasks)
        successful_results = [result for result in results if result]
        return successful_results

    # Run the asynchronous batch processing
    return asyncio.run(run_batch())


async def main(
    input_file,
    input_key,
    batch_size,
    max_workers,
    retries,
    batch_output_file,
    output_folder,
    logging_enabled,
    in_batch_concurrency,
):
    """
    Run financial health analysis by processing multiple batches in parallel.

    Uses multiprocessing and asyncio within each batch.

    Args:
        input_file (str): Path to the input JSONL file.
        input_key (str): The key in the JSONL file that contains \
            the stock ticker symbol.
        batch_size (int): Number of tickers per batch.
        max_workers (int): Number of processes for parallel \
            processing of batches.
        retries (int): Number of retry attempts for failed processes.
        batch_output_file (str): File name for the output JSONL file.
        output_folder (str): Folder for output files.
        logging_enabled (bool): Flag to enable logging.
        max_concurrent (int): Maximum number of \
            concurrent tasks within each batch.
    """
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

    tickers = [line[input_key] for line in lines if input_key in line]

    if not tickers:
        print(f"No tickers found with key '{input_key}' in the input file.")
        sys.exit(1)

    # Split tickers into batches
    batches = [(i // batch_size + 1, tickers[i : i + batch_size]) for i in range(0, len(tickers), batch_size)]

    # Create output folder if it does not exist
    os.makedirs(output_folder, exist_ok=True)

    # Path to the output file
    batch_output_path = os.path.join(output_folder, batch_output_file)

    # Remove existing output file if exists to prevent appending to old data
    if os.path.exists(batch_output_path):
        os.remove(batch_output_path)

    # Initialize ProcessPoolExecutor for parallel batch processing
    print(
        f"""
        Starting processing of {len(batches)} batches
        with up to {max_workers} parallel processes...
        """
    )
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Prepare the list of futures
        loop = asyncio.get_running_loop()
        futures = [
            loop.run_in_executor(
                executor, process_batch_sync, batch_number, batch, retries, in_batch_concurrency, logging_enabled
            )
            for batch_number, batch in batches
        ]

        # Asynchronously gather results as they complete
        for future in asyncio.as_completed(futures):
            try:
                batch_results = await future
                if batch_results:
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
                        sys.exit(1)
            except Exception as e:
                print(f"An error occurred while processing a batch: {e}")
                # Optionally, handle or log the error as needed

    print("All batches have been processed successfully.")


def parse_args():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Batch financial health analysis with\
              multiprocessing and asyncio."
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default="./sk_financial_analyst/data/inputs/tickers.jsonl",
        help="Path to the input JSONL file.",
    )
    parser.add_argument(
        "--input_key",
        type=str,
        default="ticker",
        help="The key in the JSONL file that contains the stock ticker symbol.",
    )
    parser.add_argument("--batch_size", type=int, default=4, help="Number of tickers per batch.")
    parser.add_argument(
        "--max_workers", type=int, default=4, help="Number of processes for parallel processing of batches."
    )
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts for failed processes.")
    parser.add_argument(
        "--batch_output_file", type=str, default="batch_outputs.jsonl", help="File name for the output JSONL file."
    )
    parser.add_argument(
        "--output_folder", type=str, default="./sk_financial_analyst/data/outputs", help="Folder for output files."
    )
    parser.add_argument("--logging_enabled", action="store_true", default=False, help="Enable logging.")
    parser.add_argument(
        "--in_batch_concurrency",
        type=int,
        default=4,
        help="Maximum number of concurrent \
            tasks within each batch.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(
            main(
                input_file=args.input_file,
                input_key=args.input_key,
                batch_size=args.batch_size,
                max_workers=args.max_workers,
                retries=args.retries,
                batch_output_file=args.batch_output_file,
                output_folder=args.output_folder,
                logging_enabled=args.logging_enabled,
                in_batch_concurrency=args.in_batch_concurrency,
            )
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
