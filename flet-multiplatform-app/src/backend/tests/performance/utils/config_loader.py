"""
Configuration loader with environment variable support.

This module provides functionality to load configuration from JSON files
with support for environment variable interpolation.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar, Union, overload

T = TypeVar('T', str, int, float, bool, list, dict)


def get_env_value(env_name: str, default: T, value_type: Type[T] = str) -> T:
    """Get a value from environment variables with type conversion.

    Args:
        env_name: Name of the environment variable
        default: Default value if the environment variable is not set
        value_type: Type to convert the environment variable value to

    Returns:
        The environment variable value converted to the specified type,
        or the default value if the variable is not set
    """
    if env_name not in os.environ:
        return default

    value = os.environ[env_name]

    try:
        if value_type is bool:
            # Handle boolean values (true/false, yes/no, 1/0)
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1')
            return bool(value)
        elif value_type is int:
            return int(value)
        elif value_type is float:
            return float(value)
        elif value_type is str:
            return str(value)
        elif value_type is list:
            if isinstance(value, str):
                return [item.strip() for item in value.split(',')]
            return list(value)
        elif value_type is dict:
            if isinstance(value, str):
                return json.loads(value)
            return dict(value)
        return value
    except (ValueError, TypeError, json.JSONDecodeError):
        return default

def resolve_env_vars(config_section: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve environment variables in a configuration section.

    Args:
        config_section: Configuration section to process

    Returns:
        A new dictionary with environment variables resolved
    """
    if not isinstance(config_section, dict):
        return config_section

    result = {}

    for key, value in config_section.items():
        # Skip environment variable definitions
        if key == 'env_vars':
            continue

        if isinstance(value, dict):
            # Recursively process nested dictionaries
            result[key] = resolve_env_vars(value)
        else:
            # Use the value as-is by default
            result[key] = value

    # Apply environment variable overrides if defined
    if 'env_vars' in config_section and isinstance(config_section['env_vars'], dict):
        for var_name, var_config in config_section['env_vars'].items():
            if not isinstance(var_config, dict) or 'env' not in var_config:
                continue

            env_name = var_config['env']
            default_value = var_config.get('default')
            value_type = type(default_value) if 'default' in var_config else str

            # Get the value from environment or use the default
            env_value = get_env_value(env_name, default_value, value_type)

            # Only override if the environment variable is set or has a default
            if env_value is not None:
                result[var_name] = env_value

    return result


@overload
def load_config(file_path: Union[str, Path], *, resolve_env: bool = True) -> Dict[str, Any]:
    ...

def load_config(file_path: Union[str, Path], resolve_env: bool = True) -> Dict[str, Any]:
    """Load configuration from a JSON file with environment variable support.

    Args:
        file_path: Path to the JSON configuration file
        resolve_env: Whether to resolve environment variables in the config

    Returns:
        A dictionary containing the loaded configuration

    Raises:
        FileNotFoundError: If the configuration file does not exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # Read and parse the JSON content
    with file_path.open('r', encoding='utf-8') as f:
        config = json.load(f)

    # Resolve environment variables if requested
    if resolve_env:
        config = resolve_env_vars(config)

    return config


def get_nested_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get a value from a nested dictionary using a dot-notation key path.

    Args:
        config: The configuration dictionary
        key_path: Dot-separated path to the configuration value (e.g., 'database.host')
        default: Default value to return if the key is not found

    Returns:
        The configuration value or the default if not found
    """
    keys = key_path.split('.')
    value = config

    try:
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    except (KeyError, TypeError, AttributeError):
        return default


def set_nested_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """Set a value in a nested dictionary using a dot-notation key path.

    Args:
        config: The configuration dictionary to update
        key_path: Dot-separated path to the configuration value (e.g., 'database.host')
        value: The value to set
    """
    keys = key_path.split('.')
    current = config

    for i, key in enumerate(keys[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two configuration dictionaries.

    Args:
        base: The base configuration
        override: The configuration to merge on top of the base

    Returns:
        A new dictionary containing the merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_configs(base[key], value)
        else:
            # Override the value
            result[key] = value

    return result
