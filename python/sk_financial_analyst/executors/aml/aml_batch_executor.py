"""
This script generates financial health analysis of companies.

It submits a pipeline job to Azure ML
to processes multiple batches in parallel.
"""

from azure.ai.ml import MLClient
from azure.ai.ml import Input, Output, command
from azure.ai.ml.constants import AssetTypes, InputOutputModes
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.parallel import parallel_run_function, RunFunction
from azure.ai.ml.entities import Environment
from azure.identity import DefaultAzureCredential

from dotenv import load_dotenv
import os
from pathlib import Path
import shutil
import argparse


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
    parser.add_argument(
        "--input_file_path",
        type=str,
        default="./sk_financial_analyst/data/inputs/tickers.jsonl",
        help="Path to the input JSONL file."
    )
    parser.add_argument(
        "--input_key",
        type=str,
        default="ticker",
        help="The key in the JSONL file that contains the stock ticker symbol."
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="Number of tickers per batch."
    )
    parser.add_argument(
        "--instance_count",
        type=int,
        default=1,
        help="Number of instances to run the parallel run on."
    )
    parser.add_argument(
        "--max_concurrency_per_instance",
        type=int,
        default=2,
        help="Maximum number of concurrent tasks per instance."
    )
    parser.add_argument(
        "--in_batch_concurrency",
        type=int,
        default=4,
        help="Maximum number of concurrent tasks within each batch."
    )
    parser.add_argument(
        "--batch_output_file",
        type=str,
        default="batch_outputs.jsonl",
        help="File name for the output JSONL file."
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="sk_financial_analyst_output",
        help="Folder for output files."
    )
    parser.add_argument(
        "--intermediate_folder",
        type=str,
        default="sk_financial_analyst_output/intermediate",
        help="Folder for intermediate output files."
    )
    parser.add_argument(
        "--logging_enabled",
        action="store_true",
        default=False,
        help="Enable logging."
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Number of retry attempts for failed processes."
    )
    parser.add_argument(
        "--aml_env_name",
        type=str,
        default="sk-financial-analyst-env",
        help="Name of the Azure ML environment."
    )
    parser.add_argument(
        "--cluster_name",
        type=str,
        default="cpu-cluster",
        help="Name of the Azure ML compute cluster."
    )
    parser.add_argument(
        "--experiment_name",
        type=str,
        default="sk_financial_analyst_parallel_run",
        help="Name of the Azure ML experiment."
    )
    return parser.parse_args()


def split_jsonl_into_batches(input_file_path, batch_size, temp_folder):
    """
    Split a JSONL file into batches and saves each batch into separate files.

    Args:
        input_file (str): Path to the input JSONL file.
        batch_size (int): Number of lines per batch.
        output_dir (str): Directory to save batch files. Defaults to 'temp'.
    """
    # Ensure the output directory exists, and clear its contents
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    Path(temp_folder).mkdir(parents=True, exist_ok=True)

    with open(input_file_path, "r") as infile:
        batch = []
        batch_number = 1
        for line in infile:
            batch.append(line.strip())
            if len(batch) == batch_size:
                output_file = os.path.join(
                    temp_folder, f"batch_{batch_number}.jsonl"
                )
                with open(output_file, "w") as outfile:
                    outfile.write("\n".join(batch))
                batch = []
                batch_number += 1

        # Save any remaining lines as the last batch
        if batch:
            output_file = os.path.join(
                temp_folder, f"batch_{batch_number}.jsonl"
            )
            with open(output_file, "w") as outfile:
                outfile.write("\n".join(batch))


def main():
    """
    Run financial health analysis by processing multiple batches in parallel.

    Uses Azure ML parallel run and asyncio within each batch.
    """
    args = parse_args()
    load_dotenv(override=True)

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AML_RESOURCE_GROUP_NAME")
    workspace = os.getenv("AML_WORKSPACE_NAME")

    ml_client = MLClient(
        DefaultAzureCredential(), subscription_id, resource_group, workspace
    )

    # Define the environment
    try:
        environments = ml_client.environments.list(args.aml_env_name)
        env = environments.next()
    except Exception:
        docker_env = Environment(
            name=args.aml_env_name,
            description="Environment for the financial analyst application",
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
            conda_file="./sk_financial_analyst/executors/aml/aml_env.yaml"
        )
        env = ml_client.environments.create_or_update(docker_env)

    split_jsonl_into_batches(
        input_file_path=args.input_file_path,
        batch_size=args.batch_size,
        temp_folder="./sk_financial_analyst/data/intermediate/temp"
    )

    inputs = {
        "input_folder": Input(
            type=AssetTypes.URI_FOLDER,
            path="./sk_financial_analyst/data/intermediate/temp",
            mode=InputOutputModes.RO_MOUNT
        ),
    }
    output_folder_path = os.path.join(
        "azureml://datastores/workspaceblobstore/paths",
        args.intermediate_folder
    )
    outputs = {
        "output_folder": Output(
            type=AssetTypes.URI_FOLDER,
            path=output_folder_path ,
            mode=InputOutputModes.RW_MOUNT
        )
    }

    batch_output_file = args.batch_output_file
    logging_enabled = args.logging_enabled
    in_batch_concurrency = args.in_batch_concurrency
    input_key = args.input_key
    retries = args.retries

    program_arguments = "--output_folder ${{outputs.output_folder}}"

    program_arguments += f" --batch_output_file {batch_output_file}\
    --in_batch_concurrency {in_batch_concurrency}\
    --input_key {input_key}\
    --retries {retries}"

    program_arguments += " --logging_enabled" if logging_enabled else ""

    process_batch_step = parallel_run_function(
        name="sk_financial_analyst",
        display_name="SK Financial Analyst - Parallel Run",
        description="Generates financial health analysis of companies",
        inputs=inputs,
        outputs=outputs,
        input_data="${{inputs.input_folder}}",
        instance_count=args.instance_count,
        max_concurrency_per_instance=args.max_concurrency_per_instance,
        mini_batch_size="1",
        mini_batch_error_threshold=1,
        logging_level="DEBUG",
        retry_settings=dict(max_retries=3, timeout=600),
        is_deterministic=False,
        task=RunFunction(
            code=".",
            entry_script="./sk_financial_analyst/executors/aml/process_batches_step.py",
            environment=env,
            program_arguments=program_arguments
        )
    )

    inputs = {
        "input_folder": Input(
            type=AssetTypes.URI_FOLDER,
            mode=InputOutputModes.RO_MOUNT
        )
    }
    output_folder_path = os.path.join(
        "azureml://datastores/workspaceblobstore/paths",
        args.output_folder
    )
    output_file_path = os.path.join(
        output_folder_path,
        args.batch_output_file
    )
    outputs = {
        "output_file": Output(
            type=AssetTypes.URI_FILE,
            path=output_file_path
        )
    }

    aggregate_results_step = command(
        name="aggregate_results",
        display_name="Aggregate JSONL Results",
        description="Aggregates the output JSONL files into a single file.",
        command="python ./sk_financial_analyst/executors/aml/aggregate_results_step.py --input_folder ${{inputs.input_folder}} --output_file ${{outputs.output_file}}",
        inputs=inputs,
        outputs=outputs,
        environment=env,
        code="."
    )

    @pipeline()
    def parallel_pipeline():
        step1 = process_batch_step()
        step2 = aggregate_results_step(
            input_folder=step1.outputs.output_folder
        )
        return {
            "aggregated_output": step2.outputs.output_file,
        }

    pipeline_job = parallel_pipeline()

    pipeline_job.settings.default_compute = args.cluster_name
    pipeline_job.settings.force_rerun = True

    job = ml_client.jobs.create_or_update(
        pipeline_job,
        experiment_name=args.experiment_name
    )
    ml_client.jobs.stream(job.name)


if __name__ == "__main__":
    main()
