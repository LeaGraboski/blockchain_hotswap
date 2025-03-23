# Blockchain Node Provider Hotswap

A service that streams blockchain blocks from multiple providers (Alchemy and Chainstack) and automatically switches between them when issues are detected.

## Features

- Connect to multiple blockchain node providers (Alchemy, Chainstack)
- Continuously fetch and process blockchain blocks in sequential order
- Automatically detect and switch between providers based on:
  - Block delays
  - Block validation failures
  - Provider response times
  - Connection errors
- Structured logging of block data
- Configurable health monitoring and switching thresholds

## Requirements

- Python 3.10+
- Docker (for containerized deployment)

## Quick Start

### Environment Setup

1. Set your Alchemy API key in the environment:

```bash
export ALCHEMY_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
```

2. Chainstack is pre-configured with a public endpoint, but you can customize it:

```bash
export CHAINSTACK_URL="https://nd-422-757-666.p2pify.com/0a9d79d93fb2f4a4b1e04695da2b77a7/"
```

### Running with Docker

Build and run the application with Docker:

```bash
# Build the Docker image
docker build -t blockchain_hotswap .

# Run the container
docker run -e ALCHEMY_URL="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY" blockchain-hotswap
```

### Running Locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python -m src.main
```

## Configuration

Configuration can be provided via environment variables or a `config.json` file:

```json
{
  "expected_block_time": 12,
  "max_block_processing_time": 5,
  "max_avg_response_time": 2.0,
  "error_threshold": 3,
  "min_switch_interval": 30,
  "default_provider": "alchemy",
  "providers": {
    "alchemy": {
      "url": "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
    },
    "chainstack": {
      "url": "https://nd-422-757-666.p2pify.com/0a9d79d93fb2f4a4b1e04695da2b77a7/"
    }
  }
}
```

## Running Tests

```bash
# Run all tests
python -m unittest discover

# Run specific test
python -m unittest tests.test_provider_switching
```

## Monitoring in Production

### Metrics to Track

1. **Block Processing Metrics:**
   - Block processing time
   - Block delay (time between block creation and processing)
   - Number of blocks processed per minute
   - Gaps in block sequence

2. **Provider Health Metrics:**
   - Response times
   - Error rates by provider
   - Provider switch events
   - Time spent on each provider

3. **System Health:**
   - CPU and memory usage
   - Network I/O
   - Application restarts

### Monitoring Tools

For a production deployment, the following monitoring setup would be ideal:

1. **Prometheus**: For metrics collection
   - Custom metrics for block processing and provider health
   - System metrics

2. **Grafana**: For visualization
   - Provider performance dashboards
   - Block processing dashboards
   - Alerting on critical metrics

3. **ELK Stack (Elasticsearch, Logstash, Kibana)**: For log management
   - Centralized log collection
   - Search and analysis of block data
   - Error pattern detection

### Future Improvements

1. **Enhanced Provider Management:**
   - Support for more providers (Infura, QuickNode, etc.)
   - Weighted provider selection based on historical performance
   - Automatic recovery and testing of failed providers

2. **Advanced Block Handling:**
   - Block integrity verification (full transaction validation)
   - Reorg detection and handling
   - Custom handling for specific chain events

3. **System Improvements:**
   - Distributed processing with worker pools
   - Database storage for block data
   - High availability setup with multiple instances
   - REST API for monitoring and management

4. **Additional Features:**
   - Custom webhooks for critical events
   - Transaction monitoring and filtering
   - Support for multiple blockchain networks
