"""
Hotswap mechanism module responsible for monitoring provider health
and switching between providers when needed.
"""
import logging
import time
from typing import Dict, Any
import statistics

from src.provider import Provider
from src.utils.config import ProviderName


class HotswapMechanism:
    """
    Mechanism to monitor provider health and switch between providers.
    """

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.providers = self._initialize_providers()
        self.active_provider_name = config.get('default_provider', ProviderName.ALCHEMY)
        self.active_provider = self.providers.get(self.active_provider_name)

        # Health monitoring
        self.response_times = {}
        self.error_counts = {}
        self.last_switch_time = time.time()

        self._initialize_monitor_data_for_providers()

        self.logger.info(f"Hotswap mechanism initialized with active provider: {self.active_provider_name}")

    def _initialize_providers(self) -> Dict[str, Any]:
        """
        Initialize all configured providers.

        Returns:
            Dict: Dictionary of provider name to provider instance
        """
        providers = {}
        provider_configs = self.config.get('providers', {})

        for provider_name, provider_config in provider_configs.items():
            try:
                provider = Provider(provider_config, provider_name)
                providers[provider_name] = provider
                self.logger.info(f"Initialized provider: {provider_name}")
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize provider {provider_name}: {str(e)}")

        if not providers:
            raise ValueError("No valid providers configured")

        return providers

    def _initialize_monitor_data_for_providers(self):
        '''
        Initialize monitoring data for all providers
        '''
        for provider_name in self.providers:
            self.response_times[provider_name] = []
            self.error_counts[provider_name] = 0

    def get_active_provider(self):
        """
        Get the currently active provider.

        Returns:
            Provider: The active provider instance
        """
        return self.active_provider

    def switch_provider(self, reason: str) -> None:
        """
        Switch to a different provider.

        Args:
            reason: The reason for switching providers
        """
        # Avoid switch too frequently
        min_switch_interval = self.config.get('min_switch_interval', 30)
        if time.time() - self.last_switch_time < min_switch_interval:
            self.logger.info("Not switching provider: minimum interval not reached")
            return

        # Find the next available provider
        current_provider_name = self.active_provider_name
        available_providers = [name for name, provider in
                               self.providers.items()
                               if
                               name != current_provider_name and self._is_provider_healthy(name)]

        if not available_providers:
            self.logger.warning("No healthy alternative providers available")
            return

        # Select the provider with the least errors or best performance
        next_provider_name = min(available_providers,
                                 key=lambda name: self.error_counts.get(name,
                                                                        0))

        # Switch to the new provider
        self.active_provider_name = next_provider_name
        self.active_provider = self.providers[next_provider_name]
        self.last_switch_time = time.time()

        self.logger.warning(
            f"Switched provider from {current_provider_name} to {next_provider_name}. Reason: {reason}")

    def report_performance_issue(self, issue_type: str, value: Any) -> None:
        """
        Report a performance issue with the current provider.

        Args:
            issue_type: Type of issue (e.g., 'slow_response', 'block_delay')
            value: Value associated with the issue
        """
        provider_name = self.active_provider_name

        if issue_type == 'slow_processing':
            self.response_times[provider_name].append(value)
            # Keep only the last N measurements
            max_measurements = self.config.get('max_measurements', 10)
            if len(self.response_times[provider_name]) > max_measurements:
                self.response_times[provider_name] = self.response_times[provider_name][-max_measurements:]

            # Check if average response time is too high
            if len(self.response_times[provider_name]) >= 3:
                avg_time = statistics.mean(self.response_times[provider_name])
                max_avg_time = self.config.get('max_avg_response_time', 2.0)
                if avg_time > max_avg_time:
                    self.logger.warning(f"Provider {provider_name} has high average response time: {avg_time:.2f}s")
                    self.switch_provider(f"High average response time: {avg_time:.2f}s")

        elif issue_type == 'error':
            self.error_counts[provider_name] += 1
            error_threshold = self.config.get('error_threshold', 3)
            if self.error_counts[provider_name] >= error_threshold:
                self.logger.warning(f"Provider {provider_name} reached error threshold: {self.error_counts[provider_name]}")
                self.switch_provider(f"Error threshold reached: {self.error_counts[provider_name]}")

    def _is_provider_healthy(self, provider_name: str) -> bool:
        """
        Check if a provider is healthy.

        Args:
            provider_name: Name of the provider to check

        Returns:
            bool: True if provider is healthy, False otherwise
        """
        provider = self.providers.get(provider_name)
        if not provider:
            return False

        try:
            # Simple health check - try to get the latest block number
            provider.get_latest_block_number()
            return True
        except Exception as e:
            self.logger.warning(f"Provider {provider_name} health check failed: {str(e)}")
            return False
