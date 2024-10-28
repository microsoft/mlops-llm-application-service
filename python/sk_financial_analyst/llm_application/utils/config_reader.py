"""This module contains utility functions for reading configuration files."""

import yaml
import os


def load_yaml(file_path):
    """Load a YAML file."""
    with open(file_path, 'r') as stream:
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
