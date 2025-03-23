"""
Block streaming service module responsible for continuously fetching
blockchain blocks and implementing the hotswap mechanism.
"""
import logging
import time
import json
from typing import Dict, Any
from src.hotswap_mechanism import HotswapMechanism


class BlockStreamingService:
    """
    Service that streams blockchain blocks and manages provider hotswapping.
    """
    DEFAULT_BLOCK_TIME = 12
    REQUIRED_FIELDS = ['number', 'hash', 'parentHash', 'timestamp']

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.hotswap = HotswapMechanism(config)
        self.running = False
        self.last_block_number = None
        self.expected_block_time = config.get('expected_block_time',
                                              self.DEFAULT_BLOCK_TIME)

    def start_streaming(self) -> None:
        """Start streaming blocks from the blockchain."""
        self.running = True
        self.logger.info("Block streaming started")

        while self.running:
            try:
                # Get current active provider
                provider = self.hotswap.get_active_provider()

                # Get latest block number
                latest_block = provider.get_latest_block_number()

                # Process blocks sequentially
                self._process_blocks_sequentially(provider, latest_block)

                # Short sleep to prevent high CPU usage
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(f"Error in streaming loop: {str(e)}")
                self.hotswap.switch_provider(f"Exception: {str(e)}")
                time.sleep(2)  # Give some time before reconnecting

    def _process_blocks_sequentially(self, provider,
                                     latest_block: int) -> None:
        """
        Process blocks sequentially, ensuring no gaps.

        Args:
            provider: The blockchain provider to use
            latest_block: The latest block number available
        """
        if self.last_block_number is None:
            self.last_block_number = latest_block - 1
        # For validate hashing sequence
        previous_hash = None

        for block_num in range(self.last_block_number + 1, latest_block + 1):
            start_time = time.time()
            try:
                block_data = provider.get_block(block_num)
                if (not self._validate_block(block_data) or
                        (previous_hash and not self._validate_hashing(previous_hash, block_data))):
                    self.logger.warning(f"Block {block_num} validation failed")
                    self.hotswap.switch_provider(
                        f"Block validation failed for block {block_num}")
                    return

                self._log_block_data(block_num, block_data)

                # Update last processed block
                self.last_block_number = block_num

                # Check block timing
                processing_time = time.time() - start_time
                if processing_time > self.config.get('max_block_processing_time', 5):
                    self.logger.warning(f"Block {block_num} processing took {processing_time:.2f}s")
                    # Consider switching provider if consistently slow
                    self.hotswap.report_performance_issue("slow_processing", processing_time)
                previous_hash = block_data.get('hash')

            except Exception as e:
                self.logger.error(f"Error processing block {block_num}: {str(e)}")
                self.hotswap.switch_provider(f"Error processing block {block_num}: {str(e)}")
                return

    def _validate_block(self, block_data: Dict[str, Any]) -> bool:
        """
        Validate block data integrity.

        Args:
            block_data: The block data to validate

        Returns:
            bool: True if block data is valid, False otherwise
        """
        for field in self.REQUIRED_FIELDS:
            if field not in block_data:
                self.logger.warning(
                    f"Missing required field: {field} in block data")
                return False
        return True

    def _validate_hashing(self, previous_hash: str, current_block):
        """
        Validate hashing sequence -
        previous_hash should be equal to current_block parent hash

        Args:
            block_data: The block data to validate
            previous_hash: The previous hash

        Returns:
            bool: True if block data is valid, False otherwise
        """
        if current_block.get('parentHash') == previous_hash:
            return True
        self.logger.warning(f"Hashing previous hash is not compatible with perant hash of current block")
        return False

    def _log_block_data(self, block_num: int,
                        block_data: Dict[str, Any]) -> None:
        """
        Log block data in a structured format.

        Args:
            block_num: Block number
            block_data: Block data to log
        """
        log_data = {
            'block_number': block_num,
            'timestamp': block_data.get('timestamp'),
            'hash': block_data.get('hash').hex(),
            'parent_hash': block_data.get('parentHash').hex(),
            'transaction_count': len(block_data.get('transactions', [])),
        }

        # Log as JSON
        self.logger.info(f"Block {block_num}: {json.dumps(log_data)}")

    def stop_streaming(self) -> None:
        """Stop the block streaming service."""
        self.running = False
        self.logger.info("Block streaming stopped")