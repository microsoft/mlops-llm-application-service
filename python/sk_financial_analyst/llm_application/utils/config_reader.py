"""This module contains utility functions for reading configuration files."""

import os

import yaml
from dotenv import load_dotenv


def load_yaml():
    """Load a YAML file."""
    cwd = os.getcwd()

    CONFIG_PATH = os.path.join(cwd, "llm_application/config.yaml")
    ENV_PATH = os.path.join(cwd, "llm_application/.env")
    load_dotenv(f"{ENV_PATH}")
    with open(f"{CONFIG_PATH}", "r") as stream:
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
