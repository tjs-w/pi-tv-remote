# CEC Adapter Testing with Real TV Hardware

This directory contains pytest-based tests for the CECAdapter class using real TV hardware over HDMI-CEC.

## Key Features

- Comprehensive tests for CEC adapter functionality
- Works with real TV hardware via HDMI-CEC
- Support for deployment and testing on Raspberry Pi
- Configurable test options (skip standby, debug mode, etc.)
- Graceful handling of environments without TV hardware

## Test Files

- `test_cec_adapter_real_tv.py` - Main test file for testing the CECAdapter with a real TV
- `conftest.py` - pytest configuration and fixtures
- `run_tests.sh` - Helper script to run the tests with various options
- `deploy_and_test_on_pi.sh` - Script to deploy and test on a Raspberry Pi

## Running the Tests

### Using the Helper Script

```bash
# Run all tests
./run_tests.sh

# Skip tests that put the TV in standby mode
./run_tests.sh --skip-standby

# Skip all real TV tests (when no TV is connected)
./run_tests.sh --no-tv

# Run with more verbose output
./run_tests.sh --debug
```

### Using pytest Directly

```bash
# Run all tests
pytest -v test_cec_adapter_real_tv.py

# Skip tests that put the TV in standby mode
pytest -v --skip-standby test_cec_adapter_real_tv.py

# Skip all real TV tests (when no TV is connected)
NO_TV=1 pytest -v test_cec_adapter_real_tv.py
```

## Testing on a Raspberry Pi

Since CEC functionality requires actual hardware, testing on a Raspberry Pi connected to a TV via HDMI is the best approach. Use the provided deployment script:

```bash
# Deploy and test on a Raspberry Pi (default hostname: pi.local)
./deploy_and_test_on_pi.sh

# Deploy to a specific Raspberry Pi IP address
./deploy_and_test_on_pi.sh 192.168.1.100

# Install dependencies first (recommended for fresh setup)
./deploy_and_test_on_pi.sh pi.local --install-deps

# Skip standby tests to keep the TV on
./deploy_and_test_on_pi.sh --skip-standby

# Get more detailed test output
./deploy_and_test_on_pi.sh --debug
```

The deployment script:

1. Creates a virtual environment on the Raspberry Pi
2. Installs required dependencies (if requested)
3. Copies the code to the Pi
4. Runs the tests with the specified options

### Prerequisites for Raspberry Pi

- Python 3.x installed
- SSH access enabled
- TV connected via HDMI cable
- CEC enabled on the TV

## Test Design Principles

1. **Isolation**: Tests are designed to be independent of each other, allowing for partial test runs
2. **Real Hardware**: These tests interact with real TV hardware over HDMI-CEC
3. **Graceful Skipping**: Tests are skipped gracefully if hardware is not available
4. **Minimal Side Effects**: Tests minimize side effects like leaving the TV in standby mode

## Features Tested

- CEC initialization
- TV power control (on/standby)
- Setting as active source
- Volume control
- Remote button presses
- Direct CEC command transmission

## Environment Variables

- `NO_TV` - Set this to any value to skip real TV tests
