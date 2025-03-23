"""
Configuration module for loading and validating application config.
"""
import os
import json
import logging
from typing import Dict, Any


class ProviderName:
    ALCHEMY = 'alchemy'
    CHAINSTACK = 'chainstack'


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables or default config file.

    Returns:
        Dict: Configuration dictionary
    """
    logger = logging.getLogger(__name__)

    # Default configuration time in seconds
    default_config = {
        'expected_block_time': 12,
        'max_block_processing_time': 5,
        'max_avg_response_time': 2.0,
        'error_threshold': 3,
        'min_switch_interval': 30,
        'default_provider': ProviderName.ALCHEMY,
        'providers': {
            ProviderName.ALCHEMY: {
                'url': os.environ.get('ALCHEMY_URL', 'https://base-mainnet.g.alchemy.com/v2/RbfIts-wSo38hxxm1pb9uNYx_XcOfjVQ')
            },
            ProviderName.CHAINSTACK: {
                'url': os.environ.get('CHAINSTACK_URL',
                                      'https://base-mainnet.core.chainstack.com/6c202b93c84d797aaccd2991e33bf5b3')
            }
        }
    }

    # Try to load config from file
    config_path = os.environ.get('CONFIG_PATH', 'config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Merge file config with default config
                deep_merge(default_config, file_config)
                logger.info(f"Loaded configuration from {config_path}")
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {str(e)}")

    # Override with environment variables
    if os.environ.get('ALCHEMY_URL'):
        default_config['providers'][ProviderName.ALCHEMY]['url'] = os.environ.get(
            'ALCHEMY_URL')

    if os.environ.get('CHAINSTACK_URL'):
        default_config['providers'][ProviderName.CHAINSTACK]['url'] = os.environ.get(
            'CHAINSTACK_URL')

    # Validate config
    validate_config(default_config)

    return default_config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    providers = config.get('providers', {})

    if not providers:
        raise ValueError("No providers configured")

    default_provider = config.get('default_provider')
    if default_provider not in providers:
        raise ValueError(f"Default provider '{default_provider}' not found in providers configuration")

    # Ensure at least one provider has a URL
    for provider_name, provider_config in providers.items():
        if not provider_config.get('url'):
            raise ValueError(f"Provider '{provider_name}' is missing URL configuration")


def deep_merge(dest: Dict[str, Any], src: Dict[str, Any]) -> None:
    """
    Deep merge two dictionaries.

    Args:
        dest: Destination dictionary
        src: Source dictionary
    """
    for key, value in src.items():
        if key in dest and isinstance(dest[key], dict) and isinstance(value, dict):
            deep_merge(dest[key], value)
        else:
            dest[key] = value