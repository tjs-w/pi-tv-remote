<!-- RPi Logo -->
<p align="center">
  <img src="https://www.raspberrypi.org/app/uploads/2018/03/RPi-Logo-Reg-SCREEN.png" alt="Raspberry Pi Logo" width="120"/>
</p>

<h1 align="center">Pi TV Remote</h1>

<p align="center">
  <img src="https://img.shields.io/badge/raspberry%20pi-compatible-c51a4a" alt="Raspberry Pi Compatible"/>
  <img src="https://img.shields.io/badge/hdmi--cec-enabled-3e9bcd" alt="HDMI-CEC Enabled"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"/>
  <img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="Python 3.7+"/>
</p>

<p align="center">
  Control your TV from your Raspberry Pi application using the TV's own remote via HDMI-CEC.
</p>

---

## 🔍 Overview

Pi TV Remote is a Python module that enables your Raspberry Pi applications to interface with TV remote controls via HDMI-CEC. This library makes it easy to:

- **Receive** button presses from the TV remote in your Python app
- **Send** standard TV remote commands to control the TV
- Create seamless integrations between your Pi app and the TV

Perfect for media centers, smart home displays, information kiosks, or any project where you want to control your application with the TV's existing remote.

## ✨ Features

- 📡 **Bi-directional Communication**: Receive and send TV remote commands
- 🧩 **Simple Python API**: Easy integration into existing Python projects
- 🖥️ **Command-line Interface**: Test and debug CEC connections quickly
- 🛠️ **Extensible Design**: Build on top of the core functionality
- 📺 **TV Control**: Power on/off, volume control, and navigation

## 📋 Requirements

- Raspberry Pi (any model with HDMI port)
- TV with HDMI-CEC support
- Python 3.7+
- libCEC libraries

## 📦 Installation

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

# Install the package (will automatically handle dependencies)
pip install -e .
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

## 🚀 Usage

### Command-Line Interface

Test your CEC connection and observe remote control events directly from the command line:

```bash
python -m pi_tv_remote.cli --name "MyPi" --duration 60
```

**Options:**

- `--name NAME` - Set the OSD name of the device (default: RaspberryPi)
- `--duration SECONDS` - Run for a specified number of seconds (default: run indefinitely)
- `--help` - Show help message and exit

### Python API

Integrate the CEC adapter into your own Python applications:

```python
from pi_tv_remote.cec_adapter import CECAdapter, CECConfig, RemoteButton

# Create configuration
config = CECConfig(device_name="MyPi")

# Initialize adapter
adapter = CECAdapter(config)
adapter.init()

# Listen for remote button presses
def on_button_press(key_code, duration):
    print(f"Button {key_code} pressed for {duration}ms")
    
    # Example: Map specific buttons to actions
    if key_code == RemoteButton.UP:
        print("Up navigation")
    elif key_code == RemoteButton.SELECT:
        print("Selected item")

adapter.add_keypress_callback(on_button_press)

# Send commands to the TV
adapter.power_on_tv()
adapter.send_remote_button(RemoteButton.VOLUME_UP)
adapter.standby_tv()
```

## 📁 Project Structure

```
pi_tv_remote/         # Main package directory
├── __init__.py       # Package initialization
├── cec_adapter.py    # Core CEC adapter implementation
├── cec_utils.py      # Utility functions for CEC
└── cli.py            # Command-line interface
```

## 🛠️ Development

```bash
# Format code
black pi_tv_remote
isort pi_tv_remote

# Run static type checking
mypy pi_tv_remote
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Built with ❤️ for Raspberry Pi enthusiasts
</p>
