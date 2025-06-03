<!-- RPi Logo -->
<p align="center">
  <img src="https://www.raspberrypi.org/app/uploads/2018/03/RPi-Logo-Reg-SCREEN.png" alt="Raspberry Pi Logo" width="120"/>
</p>

# Pi TV Remote

A Python module to interface your Raspberry Pi application (connected to a TV) with the TV remote via HDMI-CEC. This library allows your RPi app to receive and send remote control commands, enabling seamless integration of TV remote control into your own projects. A command-line interface (CLI) is also available for running the adapter and seeing button events.

## Features

- Receive button presses from the TV remote in your Python app
- Send standard TV remote commands (power, volume, navigation) to the TV
- Simple, extensible Python API for integration into your own RPi projects
- Command-line interface (CLI) for running the adapter and observing button events
- Real TV hardware functional testing framework
- Designed for use on Raspberry Pi with HDMI-CEC enabled TVs

## Requirements

- Raspberry Pi (any model with HDMI port)
- TV with HDMI-CEC support
- Python 3.8+
- libCEC libraries

## Installation

### On Raspberry Pi

```bash
# Install libCEC development libraries
sudo apt-get update
sudo apt-get install libcec-dev python3-dev build-essential python3-venv

# Clone the repository
git clone https://github.com/yourusername/pi-tv-remote.git
cd pi-tv-remote

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package in development mode
pip install -e .

# Install the CEC Python module
pip install cec
```

### For Development (macOS/Linux)

```bash
# Clone the repository
git clone https://github.com/yourusername/pi-tv-remote.git
cd pi-tv-remote

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Command-Line Interface (CLI)

You can run the CEC adapter and see button events directly from the command line:

```bash
python -m pi_tv_remote.cli --name "MyPi" --duration 60
```

**Options:**

- `--name NAME` &nbsp;&nbsp;&nbsp;&nbsp;Set the OSD name of the device (default: RaspberryPi)
- `--duration SECONDS` &nbsp;&nbsp;Run for a specified number of seconds (default: run indefinitely)
- `--help` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show help message and exit

This will print button events and adapter status to the console. Use this for quick diagnostics or to observe remote control events.

### Python API

The main API is available via `pi_tv_remote.cec_adapter`:

```python
from pi_tv_remote.cec_adapter import CECAdapter, CECConfig, RemoteButton

# Create configuration
config = CECConfig(device_name="MyPi")

# Initialize adapter
adapter = CECAdapter(config)
adapter.init()

# Listen for remote button presses in your app
# (see test_remote_listener.py for a real example)

def on_button_press(key_code, duration):
    print(f"Button {key_code} pressed for {duration}ms")

adapter.add_keypress_callback(on_button_press)

# Send commands to the TV
adapter.power_on_tv()
adapter.send_remote_button(RemoteButton.VOLUME_UP)
adapter.standby_tv()
```

## Functional Testing with Real TV Hardware

This project includes a comprehensive functional testing framework for the CEC adapter with real TV hardware. **These are functional tests, not unit tests, and require a real Raspberry Pi and TV with HDMI-CEC enabled.**

```bash
# From the project root
cd pi_tv_remote/tests

# Run all tests (requires a connected TV)
./run_tests.sh

# Skip tests that put the TV in standby mode
./run_tests.sh --skip-standby

# Skip all real TV tests (when no TV is connected)
./run_tests.sh --no-tv
```

### Testing on a Raspberry Pi

For testing on a Raspberry Pi with a real TV:

```bash
# From the tests directory
./deploy_and_test_on_pi.sh

# Deploy to a specific Raspberry Pi IP address
./deploy_and_test_on_pi.sh 192.168.1.100

# Install dependencies on the Pi
./deploy_and_test_on_pi.sh --install-deps
```

See `pi_tv_remote/tests/README.md` for more detailed testing information and options.

## Project Structure

```
pi_tv_remote/             # Main package directory
├── __init__.py           # Package initialization
├── cec_adapter.py        # Core CEC adapter implementation
├── cec_utils.py          # Utility functions for CEC
├── cli.py                # Command-line interface
```

> **Note:** All functional test and test utility files (the `tests/` directory and `test_tools/`) have been removed from the codebase. For testing, refer to previous releases or your own test setup.

## Development

```bash
# Run tests (requires real TV hardware)
cd pi_tv_remote/tests
./run_tests.sh

# Format code
black pi_tv_remote
isort pi_tv_remote
```

## License

MIT
