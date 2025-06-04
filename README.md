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
- 🔌 **Multiple TV Support**: Compatible with various TV manufacturers including LG, Samsung, and Sony

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

### Advanced Usage: Command Callbacks and TV Control

```python
from pi_tv_remote.cec_adapter import CECAdapter, CECConfig, RemoteButton, CECCommand

# Create and initialize the adapter
adapter = CECAdapter(CECConfig(device_name="MyDevice"))
adapter.init()

# Register for TV→RPi commands
def handle_power_status_request(opcode, from_addr, to_addr, parameters):
    print("TV is checking if we're on!")
    # Custom logic before default response

# Add a callback for when TV requests power status
adapter.add_command_callback(CECCommand.GIVE_DEVICE_POWER_STATUS, handle_power_status_request)

# Send RPi→TV commands
# Power on the TV
adapter.power_on_tv()

# Put TV in standby
adapter.standby_tv()

# Set this device as active source
adapter.set_active_source()

# Send remote button presses
adapter.send_remote_button(RemoteButton.UP)
adapter.send_remote_button(RemoteButton.SELECT)

# Request information from TV
adapter.request_power_status()
adapter.request_vendor_id()

# Send any arbitrary CEC command
adapter.send_command(CECCommand.VENDOR_COMMAND, 
                    destination=0, # TV address
                    parameters=b'\x01\x02\x03')

adapter.run()
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

# Run tests
./run_tests
```

## 📚 CEC Button Reference

The following buttons are supported by default:

| Button | Code | Symbol | Description |
|--------|:----:|:------:|-------------|
| UP | 0x01 | ⬆️ | Navigate up |
| DOWN | 0x02 | ⬇️ | Navigate down |
| LEFT | 0x03 | ⬅️ | Navigate left |
| RIGHT | 0x04 | ➡️ | Navigate right |
| SELECT | 0x00 | ⏺️ | Confirm selection |
| BACK | 0x0D | 🔙 | Return/exit |
| PLAY | 0x44 | ▶️ | Start playback |
| STOP | 0x45 | ⏹️ | Stop playback |
| PAUSE | 0x46 | ⏸️ | Pause playback |
| REWIND | 0x48 | ⏪ | Rewind content |
| FAST_FORWARD | 0x49 | ⏩ | Fast forward |
| BLUE | 0x71 | 🔵 | Blue function button |
| RED | 0x72 | 🔴 | Red function button |
| GREEN | 0x73 | 🟢 | Green function button |
| YELLOW | 0x74 | 🟡 | Yellow function button |
| NUMBER_0 to NUMBER_9 | 0x20-0x29 | 0️⃣-9️⃣ | Number keys |
| VOLUME_UP | 0x41 | 🔊 | Increase volume |
| VOLUME_DOWN | 0x42 | 🔉 | Decrease volume |
| MUTE | 0x43 | 🔇 | Mute audio |

You can define custom callbacks for these or add support for additional buttons as needed.

## 📊 CEC Command Direction Reference

This table shows HDMI-CEC commands according to the official HDMI specification and their typical implementations:

| Command | Icon | TV→RPi | RPi→TV | Description |
|---------|:----:|:------:|:------:|-------------|
| **Navigation Controls** |  |  |  | |
| UP (0x01) | ⬆️ | ✓ | ✓ | Navigate up - part of User Control Pressed (0x44) |
| DOWN (0x02) | ⬇️ | ✓ | ✓ | Navigate down - part of User Control Pressed (0x44) |
| LEFT (0x03) | ⬅️ | ✓ | ✓ | Navigate left - part of User Control Pressed (0x44) |
| RIGHT (0x04) | ➡️ | ✓ | ✓ | Navigate right - part of User Control Pressed (0x44) |
| SELECT (0x00) | ⏺️ | ✓ | ✓ | Confirm selection - part of User Control Pressed (0x44) |
| BACK/EXIT (0x0D) | 🔙 | ✓ | ✓ | Return/exit - part of User Control Pressed (0x44) |
| **Color Buttons** |  |  |  | |
| RED (0x72) | 🔴 | ✓ | ✓ | Red function button - part of User Control Pressed (0x44) |
| GREEN (0x73) | 🟢 | ✓ | ✓ | Green function button - part of User Control Pressed (0x44) |
| YELLOW (0x74) | 🟡 | ✓ | ✓ | Yellow function button - part of User Control Pressed (0x44) |
| BLUE (0x71) | 🔵 | ✓ | ✓ | Blue function button - part of User Control Pressed (0x44) |
| **Media Controls** |  |  |  | |
| PLAY (0x44) | ▶️ | ✓ | ✓ | Start playback - part of User Control Pressed (0x44) |
| STOP (0x45) | ⏹️ | ✓ | ✓ | Stop playback - part of User Control Pressed (0x44) |
| PAUSE (0x46) | ⏸️ | ✓ | ✓ | Pause playback - part of User Control Pressed (0x44) |
| REWIND (0x48) | ⏪ | ✓ | ✓ | Rewind content - part of User Control Pressed (0x44) |
| FAST_FORWARD (0x49) | ⏩ | ✓ | ✓ | Fast forward - part of User Control Pressed (0x44) |
| **Number Keys** |  |  |  | |
| NUMBER_0 (0x20) | 0️⃣ | △ | ✓ | Number key 0 - part of User Control Pressed (0x44) |
| NUMBER_1 (0x21) | 1️⃣ | △ | ✓ | Number key 1 - part of User Control Pressed (0x44) |
| NUMBER_2 (0x22) | 2️⃣ | △ | ✓ | Number key 2 - part of User Control Pressed (0x44) |
| NUMBER_3 (0x23) | 3️⃣ | △ | ✓ | Number key 3 - part of User Control Pressed (0x44) |
| NUMBER_4 (0x24) | 4️⃣ | △ | ✓ | Number key 4 - part of User Control Pressed (0x44) |
| NUMBER_5 (0x25) | 5️⃣ | △ | ✓ | Number key 5 - part of User Control Pressed (0x44) |
| NUMBER_6 (0x26) | 6️⃣ | △ | ✓ | Number key 6 - part of User Control Pressed (0x44) |
| NUMBER_7 (0x27) | 7️⃣ | △ | ✓ | Number key 7 - part of User Control Pressed (0x44) |
| NUMBER_8 (0x28) | 8️⃣ | △ | ✓ | Number key 8 - part of User Control Pressed (0x44) |
| NUMBER_9 (0x29) | 9️⃣ | △ | ✓ | Number key 9 - part of User Control Pressed (0x44) |
| **Volume Controls** |  |  |  | |
| VOLUME_UP (0x41) | 🔊 | △ | ✓ | Increase volume - typically handled by TV/audio system |
| VOLUME_DOWN (0x42) | 🔉 | △ | ✓ | Decrease volume - typically handled by TV/audio system |
| MUTE (0x43) | 🔇 | △ | ✓ | Mute audio - typically handled by TV/audio system |
| **Power Controls** |  |  |  | |
| STANDBY (0x36) | ⏻ | | ✓ | Turn off TV - RPi can send to put TV into standby |
| IMAGE_VIEW_ON (0x04) | 📺 | | ✓ | Turn on TV - RPi can power on TV |
| **Device Status** |  |  |  | |
| GIVE_POWER_STATUS (0x8F) | 🔌 | | ✓ | Query TV power status - Device Power Status feature |
| REPORT_POWER_STATUS (0x90) | 🔋 | ✓ | ✓ | Report power status - Device Power Status feature |
| **Input Controls** |  |  |  | |
| ACTIVE_SOURCE (0x82) | 📱 | ✓ | ✓ | Set device as active - One Touch Play & Routing Control |
| SET_STREAM_PATH (0x86) | 📺 | ✓ | | Request device to become active - Routing Control |
| ROUTING_CHANGE (0x80) | 🔀 | ✓ | ✓ | Change input routing - Routing Control feature |
| **Device Information** |  |  |  | |
| SET_OSD_NAME (0x47) | 📝 | | ✓ | Set device name - Device OSD Name Transfer feature |
| GIVE_OSD_NAME (0x46) | 📋 | ✓ | ✓ | Request device name - Device OSD Name Transfer feature |
| REPORT_PHYSICAL_ADDR (0x84) | 🔢 | ✓ | ✓ | Report physical address - System Information feature |
| DEVICE_VENDOR_ID (0x87) | 🏢 | ✓ | ✓ | Report vendor ID - Vendor Specific Command feature |
| **Remote Control** |  |  |  | |
| USER_CONTROL_PRESSED (0x44) | 🎮 | ✓ | ✓ | Key press - Remote Control Pass Through feature |
| USER_CONTROL_RELEASED (0x45) | 🎮 | ✓ | ✓ | Key release - Remote Control Pass Through feature |

**Legend:**  
✓ - Defined in the standard and typically implemented  
△ - Defined in the standard but inconsistently implemented by manufacturers

## ⚠️ TV Manufacturer Compatibility Notes

While the HDMI-CEC specification defines standard commands, actual implementation varies by manufacturer:

- **LG (SimpLink)**: Reliably passes navigation and media controls. Typically intercepts volume and number keys.
- **Samsung (Anynet+)**: Generally good support for standard CEC, more likely to pass volume controls.
- **Sony (BRAVIA Sync)**: Good compliance with the spec, but may have proprietary extensions.

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
