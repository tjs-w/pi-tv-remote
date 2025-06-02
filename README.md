# Pi TV Remote

A Raspberry Pi-based TV remote control application using HDMI-CEC.

## Features

- Control your TV using the Raspberry Pi via HDMI-CEC
- Support for standard TV remote commands (power, volume, navigation)
- Simple command-line interface
- Extendable API for custom applications

## Requirements

- Raspberry Pi (any model with HDMI port)
- TV with HDMI-CEC support
- Python 3.8+
- libCEC libraries

## Installation

This project uses `uv` for dependency management:

```bash
# Install libCEC development libraries (on Raspberry Pi)
sudo apt-get update
sudo apt-get install libcec-dev python3-dev build-essential

# Clone the repository
git clone https://github.com/yourusername/pi-tv-remote.git
cd pi-tv-remote

# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Install the CEC Python module
uv pip install cec
```

## Usage

### Command Line

```bash
# Run with default settings
pi-tv-remote

# Specify a custom device name
pi-tv-remote --name "MyPi"

# Run for a specific duration (in seconds)
pi-tv-remote --duration 300
```

### Python API

```python
from pi_tv_remote import CECAdapter, CECConfig, RemoteButton

# Create configuration
config = CECConfig(device_name="MyPi")

# Initialize adapter
adapter = CECAdapter(config)
adapter.init()

# Control TV
adapter.power_on_tv()
adapter.send_remote_button(RemoteButton.VOLUME_UP)
adapter.standby_tv()
```

## Development

```bash
# Run tests
pytest

# Format code
black pi_tv_remote
isort pi_tv_remote
```

## License

MIT
