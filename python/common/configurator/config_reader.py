"""This module contains utility functions for reading configuration files."""

import os

import yaml
from azure.monitor.opentelemetry import configure_azure_monitor
from common.configurator.otel import config_otel
from dotenv import load_dotenv


def load_yaml(file_path):
    """Load a YAML file."""
    load_dotenv()
    if (os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")) is not None:
        configure_azure_monitor(connection_string=os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"))
    else:
        config_otel()
    with open(file_path, "r") as stream:
        return yaml.safe_load(os.path.expandvars(stream.read()))


def get_value_by_name(config_data, *keys):
    """Get a value from the YAML file by key."""
    # Navigate through the YAML structure based on the provided keys
    value = config_data
    for key in keys:
        value = value.get(key)
        if value is None:
            raise KeyError(f"Key '{key}' not found in configuration.")
    return value
