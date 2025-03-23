"""
Unit tests for block streaming service.
"""
import unittest
from unittest.mock import MagicMock, patch
import json

from src.block_streaming_service import BlockStreamingService
from src.utils.config import ProviderName


class TestBlockStreamingService(unittest.TestCase):
    """
    Test cases for the BlockStreamingService class.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = {
            'expected_block_time': 12,
            'max_block_processing_time': 5,
            'providers': {
                ProviderName.ALCHEMY: {'url': 'mock_url'},
                ProviderName.CHAINSTACK: {'url': 'mock_url'}
            }
        }

        # Patch the HotswapMechanism in the context where it's used by BlockStreamingService
        hotswap_path = 'src.block_streaming_service.HotswapMechanism'
        self.mock_hotswap_patcher = patch(hotswap_path)
        self.mock_hotswap_class = self.mock_hotswap_patcher.start()
        self.mock_hotswap_instance = MagicMock()
        self.mock_hotswap_class.return_value = self.mock_hotswap_instance

        # Patch the Provider class in the context where it's used by BlockStreamingService
        provider_path = 'src.provider.Provider'
        self.mock_provider_patcher = patch(provider_path)
        self.mock_provider_class = self.mock_provider_patcher.start()
        self.mock_provider = MagicMock()
        self.mock_provider_class.return_value = self.mock_provider

        # Hotswap returns the mock provider
        self.mock_hotswap_instance.get_active_provider.return_value = self.mock_provider

        # Create the service
        self.service = BlockStreamingService(self.mock_config)
        self.service.running = False  # Prevent actual loops

    def tearDown(self):
        """Tear down test fixtures."""
        self.mock_hotswap_patcher.stop()
        self.mock_provider_patcher.stop()

    def test_process_blocks_sequentially(self):
        """Test that blocks are processed sequentially."""
        # Mock block data
        mock_block = {
            'number': 123,
            'hash': bytes.fromhex('1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'),
            'parentHash': bytes.fromhex('abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890'),
            'timestamp': 1647235166,
            'transactions': []
        }

        self.mock_provider.get_block.return_value = mock_block

        # Test processing a single block
        self.service._process_blocks_sequentially(self.mock_provider, 123)

        # Verify that get_block was called
        self.mock_provider.get_block.assert_called_once_with(123)

        # Verify that the last block number was updated
        self.assertEqual(self.service.last_block_number, 123)

    def test_validate_block(self):
        """Test block validation logic."""
        # Valid block
        valid_block = {
            'number': 123,
            'hash': 'hash',
            'parentHash': 'parent_hash',
            'timestamp': 1647235166
        }

        # Invalid block (missing field)
        invalid_block = {
            'number': 123,
            'hash': 'hash',
            # Missing parentHash
            'timestamp': 1647235166
        }

        # Test validation
        self.assertTrue(self.service._validate_block(valid_block))
        self.assertFalse(self.service._validate_block(invalid_block))


if __name__ == '__main__':
    unittest.main()