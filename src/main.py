"""
Main entry point for the Blockchain Node Provider Hotswap service.
"""
import logging
from src.block_streaming_service import BlockStreamingService
from src.utils.logger import setup_logger
from src.utils.config import load_config


def main():
    """Main function to start the block streaming service with hotswap capabilities."""
    # Set up logging
    setup_logger()
    logger = logging.getLogger(__name__)
    logger.info("Starting Blockchain Node Provider Hotswap Service")

    # Load configuration
    config = load_config()

    # Initialize the block streaming service
    service = BlockStreamingService(config)

    try:
        # Start streaming blocks
        service.start_streaming()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        # Ensure proper cleanup
        service.stop_streaming()
        logger.info("Service stopped")


if __name__ == "__main__":
    main()