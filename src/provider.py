import time
from typing import Dict, Any
from web3 import Web3
import logging


class Provider:
    """
    Provider implementation for Provider blockchain node.
    """

    def __init__(self, config: Dict[str, Any], provider_type: str):
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")
        self.config = config
        self.name = provider_type
        self.url = config.get('url')

        if not self.url:
            raise ValueError(f"{self.name} URL is required")

        self.web3 = Web3(Web3.HTTPProvider(self.url))
        if not self.web3.is_connected():
            raise ConnectionError(
                f"Failed to connect to {self.name} at {self.url}")

        self.logger.info(f"Connected to {self.name} at {self.url}")

    def get_latest_block_number(self) -> int:
        """
        Get the latest block number from Provider.

        Returns:
            int: The latest block number
        """
        try:
            result, execution_time = self._measure_request_time(
                lambda: self.web3.eth.block_number)
            self.logger.debug(
                f"Got latest block number from {self.name}: {result} (took {execution_time:.2f}s)")
            return result
        except Exception as e:
            self.logger.error(
                f"Error getting latest block number from {self.name}: {str(e)}")
            raise

    def get_block(self, block_number: int) -> Dict[str, Any]:
        """
        Get block data for a specific block number from Provider.

        Args:
            block_number: The block number to fetch

        Returns:
            Dict: Block data
        """
        try:
            result, execution_time = self._measure_request_time(
                self.web3.eth.get_block, block_number, full_transactions=False
            )
            self.logger.debug(
                f"Got block {block_number} from {self.name} (took {execution_time:.2f}s)")
            return result
        except Exception as e:
            self.logger.error(
                f"Error getting block {block_number} from {self.name}: {str(e)}")
            raise

    @classmethod
    def _measure_request_time(cls, func, *args, **kwargs):
        """
        Helper method to measure request execution time in order to switch
        provider if it is too slow.

        Args:
            func: Function to measure
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Tuple: (result, execution_time)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
