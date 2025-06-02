# CEC Adapter Testing with Real TV Hardware

This directory contains pytest-based tests for the CECAdapter class using real TV hardware over HDMI-CEC.

## Key Features

- Comprehensive tests for CEC adapter functionality
- Works with real TV hardware via HDMI-CEC
- Configurable test options (skip standby, debug mode, etc.)
- Graceful handling of environments without TV hardware

## Test Files

- `test_cec_adapter_real_tv.py` - Main test file for testing the CECAdapter with a real TV
- `test_remote_listener.py` - Test that detects button presses from a real TV remote
- `test_cec_adapter.py` - Basic unit tests for the CECAdapter class
- `conftest.py` - pytest configuration and fixtures

## Running the Tests

### Basic Usage

```bash
# Run all tests
pytest -v pi_tv_remote/tests/

# Skip tests that put the TV in standby mode
pytest -v --skip-standby pi_tv_remote/tests/

# Skip all real TV tests (when no TV is connected)
NO_TV=1 pytest -v pi_tv_remote/tests/

# Run specific test file
pytest -v pi_tv_remote/tests/test_cec_adapter.py
```

### Remote Button Detection Test

This test detects button presses from a real TV remote control:

```bash
# Run the remote button detection test
pytest -v pi_tv_remote/tests/test_remote_listener.py

# Run with a shorter timeout (default is 60 seconds)
REMOTE_WAIT_TIME=30 pytest -v pi_tv_remote/tests/test_remote_listener.py
```

## Testing on a Raspberry Pi

Since CEC functionality requires actual hardware, testing on a Raspberry Pi connected to a TV via HDMI is the best approach.

### Prerequisites for Raspberry Pi

- Python 3.8+ installed
- TV connected via HDMI cable
- CEC enabled on the TV
- Required libraries installed:

  ```bash
  sudo apt-get update
  sudo apt-get install libcec-dev python3-dev build-essential
  ```

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
- `REMOTE_WAIT_TIME` - Set the timeout for remote button detection (in seconds)
