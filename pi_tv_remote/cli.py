#!/usr/bin/env python3
"""
PiTVRemote - CEC adapter for Raspberry Pi.

Usage:
  python -m pi_tv_remote.cli --name "DeviceName"

Options:
  --name NAME          Set OSD name of the device (default: RaspberryPi)
  --duration SECONDS   Run for a specified number of seconds (default: run indefinitely)
  --help               Show this help message and exit
"""
import argparse
import datetime
import sys
import time
import traceback
from typing import Callable, Dict, Optional

# Import from pi_tv_remote
from pi_tv_remote.cec_adapter import log_debug  # Import the log_debug function
from pi_tv_remote.cec_adapter import CECAdapter, CECConfig, RemoteButton


def create_default_callbacks(adapter: CECAdapter) -> None:
    """Create default callbacks for all standard buttons."""
    log_debug("Setting up button callbacks", "DEBUG")
    start_time = time.time()

    def generic_handler(button_name: str, icon: str) -> Callable:
        """Create a generic button handler."""

        def handler(key_code: int, duration: int) -> None:
            log_debug(f"{icon} {button_name} button pressed (code: {hex(key_code)})")

        return handler

    # Map buttons to handler names and icons
    button_info = {
        RemoteButton.UP: ("UP", "⬆️"),
        RemoteButton.DOWN: ("DOWN", "⬇️"),
        RemoteButton.LEFT: ("LEFT", "⬅️"),
        RemoteButton.RIGHT: ("RIGHT", "➡️"),
        RemoteButton.SELECT: ("SELECT", "⏺️"),
        RemoteButton.BACK: ("BACK", "🔙"),
        RemoteButton.STOP: ("STOP", "⏹️"),
        RemoteButton.PLAY: ("PLAY", "▶️"),
        RemoteButton.PAUSE: ("PAUSE", "⏸️"),
        RemoteButton.REWIND: ("REWIND", "⏪"),
        RemoteButton.FAST_FORWARD: ("FAST_FORWARD", "⏩"),
        RemoteButton.BLUE: ("BLUE", "🔵"),
        RemoteButton.RED: ("RED", "🔴"),
        RemoteButton.GREEN: ("GREEN", "🟢"),
        RemoteButton.YELLOW: ("YELLOW", "🟡"),
        # Volume controls
        RemoteButton.VOLUME_UP: ("VOLUME_UP", "🔊"),
        RemoteButton.VOLUME_DOWN: ("VOLUME_DOWN", "🔉"),
        RemoteButton.MUTE: ("MUTE", "🔇"),
        # Number keys
        RemoteButton.NUMBER_0: ("0", "0️⃣"),
        RemoteButton.NUMBER_1: ("1", "1️⃣"),
        RemoteButton.NUMBER_2: ("2", "2️⃣"),
        RemoteButton.NUMBER_3: ("3", "3️⃣"),
        RemoteButton.NUMBER_4: ("4", "4️⃣"),
        RemoteButton.NUMBER_5: ("5", "5️⃣"),
        RemoteButton.NUMBER_6: ("6", "6️⃣"),
        RemoteButton.NUMBER_7: ("7", "7️⃣"),
        RemoteButton.NUMBER_8: ("8", "8️⃣"),
        RemoteButton.NUMBER_9: ("9", "9️⃣"),
    }

    # Create handlers for each button
    for button_code, (button_name, icon) in button_info.items():
        adapter.add_button_callback(button_code, generic_handler(button_name, icon))

    log_debug(
        f"Button callbacks setup completed in {time.time() - start_time:.2f} seconds",
        "DEBUG",
    )


def run_cec_adapter(config: CECConfig, duration: Optional[int] = None) -> None:
    """Run the CEC adapter for the specified duration or indefinitely."""
    adapter = CECAdapter(config)

    log_debug(f"Initializing CEC adapter...", "INFO")
    log_debug(f"Device name: {config.device_name}", "DEBUG")
    log_debug(f"Physical address: {config.physical_address}", "DEBUG")

    # Initialize the adapter
    if not adapter.init():
        log_debug("Failed to initialize CEC adapter", "ERROR")
        return

    # Register default button callbacks
    log_debug("Registering button callbacks", "DEBUG")
    create_default_callbacks(adapter)

    try:
        # Run indefinitely
        log_debug("Starting CEC event loop to run indefinitely", "INFO")
        adapter.run()

    except KeyboardInterrupt:
        log_debug("\nKeyboard interrupt received, exiting...", "INFO")
        print("\nExiting...")
    except Exception as e:
        log_debug(f"Error in main execution: {e}", "ERROR")
        log_debug(f"Traceback: {traceback.format_exc()}", "ERROR")
        print(f"Error: {e}")
    finally:
        log_debug("Closing CEC adapter", "DEBUG")
        adapter.cleanup()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="CEC adapter for Raspberry Pi")

    parser.add_argument(
        "--name",
        help="Set OSD name of the device (default: RaspberryPi)",
        default="RaspberryPi",
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="Run for a specified number of seconds (default: run indefinitely)",
        default=None,
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Print header
    print("\n" + "=" * 40)
    print(" PiTVRemote - CEC Adapter for Raspberry Pi")
    print("=" * 40)

    # Create configuration
    config = CECConfig(
        device_name=args.name,
    )

    # Run the adapter
    try:
        run_cec_adapter(config, args.duration)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")

    print("\nExiting PiTVRemote.")


if __name__ == "__main__":
    main()
