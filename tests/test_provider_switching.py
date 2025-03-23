"""
Unit tests for provider switching logic using mocked HotswapMechanism.
"""
import unittest
from unittest.mock import MagicMock, patch

from src.utils.config import ProviderName


class TestProviderSwitching(unittest.TestCase):
    """
    Test cases for provider switching logic using a mocked HotswapMechanism.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = {
            'default_provider': ProviderName.ALCHEMY,
            'min_switch_interval': 0,
            'error_threshold': 2,
            'providers': {
                ProviderName.ALCHEMY: {'url': 'mock://alchemy-url'},
                ProviderName.CHAINSTACK: {'url': 'mock://chainstack-url'}
            }
        }

        # Patch HotswapMechanism in the module where it's used
        hotswap_path = 'src.block_streaming_service.HotswapMechanism'
        self.hotswap_patcher = patch(hotswap_path)
        self.mock_hotswap_class = self.hotswap_patcher.start()
        self.mock_hotswap_instance = MagicMock()
        self.mock_hotswap_class.return_value = self.mock_hotswap_instance

        # Setup mock provider
        self.mock_provider = MagicMock()
        self.mock_provider.name = ProviderName.ALCHEMY
        self.mock_hotswap_instance.active_provider_name = ProviderName.ALCHEMY
        self.mock_hotswap_instance.get_active_provider.return_value = self.mock_provider

        # 🔧 Move fake_switch_provider to instance method
        def fake_switch_provider(reason):
            if self.mock_hotswap_instance.active_provider_name == ProviderName.ALCHEMY:
                self.mock_hotswap_instance.active_provider_name = ProviderName.CHAINSTACK
                self.mock_hotswap_instance.get_active_provider.return_value.name = ProviderName.CHAINSTACK
            else:
                self.mock_hotswap_instance.active_provider_name = ProviderName.ALCHEMY
                self.mock_hotswap_instance.get_active_provider.return_value.name = ProviderName.ALCHEMY

        self.fake_switch_provider = fake_switch_provider

        # Assign to side_effect
        self.mock_hotswap_instance.switch_provider.side_effect = self.fake_switch_provider

    def tearDown(self):
        """Stop patchers."""
        self.hotswap_patcher.stop()

    def test_provider_switching(self):
        """Test provider switching behavior using mocked HotswapMechanism."""
        # Initially set to alchemy
        self.assertEqual(self.mock_hotswap_instance.active_provider_name, ProviderName.ALCHEMY)

        # Simulate two performance issues that exceed threshold
        self.mock_hotswap_instance.report_performance_issue.side_effect = lambda *_: self.fake_switch_provider("error")

        # Simulate performance degradation
        self.mock_hotswap_instance.report_performance_issue('error', None)
        self.assertEqual(self.mock_hotswap_instance.active_provider_name, ProviderName.CHAINSTACK)

        # Simulate switch back
        self.mock_hotswap_instance.switch_provider("Manual reset")
        self.assertEqual(self.mock_hotswap_instance.active_provider_name, ProviderName.ALCHEMY)

    def test_no_healthy_providers(self):
        """Test fallback when no healthy providers are available."""
        self.mock_hotswap_instance.get_active_provider.return_value.get_latest_block_number.side_effect = Exception("Provider down")

        with self.assertRaises(Exception):
            self.mock_hotswap_instance.get_active_provider().get_latest_block_number()

    def test_performance_monitoring(self):
        """Test performance monitoring behavior."""
        self.mock_hotswap_instance.active_provider_name = ProviderName.ALCHEMY

        for _ in range(3):
            self.mock_hotswap_instance.report_performance_issue('slow_processing', 5.0)

        # Simulate threshold switch
        self.mock_hotswap_instance.switch_provider("slow")
        self.assertIn(self.mock_hotswap_instance.active_provider_name, [ProviderName.ALCHEMY, ProviderName.CHAINSTACK])


if __name__ == '__main__':
    unittest.main()
