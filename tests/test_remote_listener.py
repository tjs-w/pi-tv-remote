#!/usr/bin/env python3
"""
Remote Control Listener Test
This pytest module detects button presses from a real TV remote.

IMPORTANT: These are NOT unit tests. These tests require:
- A Raspberry Pi with CEC support
- A TV connected via HDMI cable with CEC enabled
- Proper libcec installation on the Raspberry Pi
- A compatible TV remote control
"""
import os
import signal
import sys
import threading
import time
from typing import Dict, List, Optional, Set

import pytest

from pi_tv_remote.cec_adapter import (
    CECAdapter,
    CECCommand,
    CECConfig,
    RemoteButton,
    cec,
    log_debug,
)

# Detected button presses will be stored here
detected_buttons: Set[int] = set()
button_event = threading.Event()
stop_listening = threading.Event()
listener_thread = None


# Set up signal handler for proper termination
def signal_handler(sig, frame):
    """Handle termination signals to clean up resources."""
    print("\nTest interrupted. Cleaning up...")
    stop_listening.set()
    if listener_thread and listener_thread.is_alive():
        listener_thread.join(timeout=2.0)
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def button_callback(key_code: int, duration: int) -> None:
    """Callback for button presses from remote."""
    global detected_buttons

    # Add the button to the detected set
    detected_buttons.add(key_code)

    # Get button name
    button_names = {
        RemoteButton.SELECT: "SELECT",
        RemoteButton.UP: "UP",
        RemoteButton.DOWN: "DOWN",
        RemoteButton.LEFT: "LEFT",
        RemoteButton.RIGHT: "RIGHT",
        RemoteButton.RED: "RED",
        RemoteButton.GREEN: "GREEN",
        RemoteButton.YELLOW: "YELLOW",
        RemoteButton.BLUE: "BLUE",
    }

    button_name = button_names.get(key_code, f"UNKNOWN (0x{key_code:02x})")
    print(f"✅ Detected button press: {button_name}")

    # Signal that a button was pressed
    button_event.set()


def command_callback(cmd, *args) -> None:
    """Callback for CEC commands that might contain button presses."""
    # Try to extract the command details
    opcode = None
    params = None
    source = None
    destination = None
    is_button_press = False
    button_code = None

    try:
        # Log all incoming commands with clear formatting
        print(f"\n=== CEC COMMAND RECEIVED ===")
        print(f"Command: {cmd}")
        print(f"Args: {args}")

        # Extract info based on the command format we're seeing
        if isinstance(cmd, dict) and "opcode" in cmd:
            # Dict format
            opcode = cmd["opcode"]
            params = cmd.get("parameters", None)
            source = cmd.get("initiator", None)
            destination = cmd.get("destination", None)
            print(f"Format: Dictionary")
        elif hasattr(cmd, "opcode"):
            # Object format with opcode attribute
            opcode = cmd.opcode
            params = getattr(cmd, "parameters", None)
            source = getattr(cmd, "initiator", None)
            destination = getattr(cmd, "destination", None)
            print(f"Format: Object with attributes")
        elif (
            isinstance(cmd, int)
            and cmd == 4
            and len(args) > 0
            and isinstance(args[0], dict)
        ):
            # Format 4 with dict in args[0] - this matches what we're seeing
            cmd_dict = args[0]
            opcode = cmd_dict.get("opcode", None)
            params = cmd_dict.get("parameters", None)
            source = cmd_dict.get("initiator", None)
            destination = cmd_dict.get("destination", None)
            print(f"Format: Format 4 with dictionary")
        elif len(args) >= 3:
            # Classic format with source, dest, opcode, params in args
            source = args[0]
            destination = args[1]
            opcode = args[2]
            params = args[3] if len(args) > 3 else None
            print(f"Format: Classic with positional args")
        else:
            # Unknown format
            print(f"Format: Unknown")
            return

        # For Format 4, check for USER_CONTROL_PRESSED (opcode 68 or 0x44)
        if opcode == 68 or opcode == CECCommand.USER_CONTROL_PRESSED:
            is_button_press = True

            # The button code is in the first byte of params
            if params and hasattr(params, "__getitem__"):
                button_code = params[0]
                print(f"✅ USER CONTROL PRESSED: Button code 0x{button_code:02x}")
                button_callback(button_code, 0)

        # Log the decoded command
        print(f"Decoded command: opcode={opcode} (0x{opcode:02x} if numeric)")
        print(f"Source: {source}, Destination: {destination}")
        print(f"Parameters: {params}")
        print(f"Is button press: {is_button_press}")
        if button_code:
            print(f"Button code: 0x{button_code:02x}")
        print("=== END COMMAND ===\n")

    except Exception as e:
        print(f"Error in command callback: {e}")
        import traceback

        traceback.print_exc()


def wait_for_buttons_thread(max_wait_time: int = 60) -> None:
    """Thread that waits for button presses."""
    start_time = time.time()

    # Brief monitoring message
    print("\nMonitoring for remote control button presses...")

    while not stop_listening.is_set() and time.time() - start_time < max_wait_time:
        # Check if button was pressed (with timeout)
        if button_event.wait(1.0):
            # Reset the event for next button press
            button_event.clear()

    # Print summary of detected buttons
    if detected_buttons:
        print("\n📊 Detection Summary:")

        # Define the expected navigation buttons
        nav_buttons = [
            (RemoteButton.UP, "UP"),
            (RemoteButton.DOWN, "DOWN"),
            (RemoteButton.LEFT, "LEFT"),
            (RemoteButton.RIGHT, "RIGHT"),
            (RemoteButton.SELECT, "SELECT"),
            (RemoteButton.PLAY, "PLAY"),
            (RemoteButton.PAUSE, "PAUSE"),
        ]

        # Define the expected color buttons
        color_buttons = [
            (RemoteButton.RED, "RED"),
            (RemoteButton.GREEN, "GREEN"),
            (RemoteButton.YELLOW, "YELLOW"),
            (RemoteButton.BLUE, "BLUE"),
        ]

        # Report on navigation buttons
        print("\nNavigation Buttons:")
        for button, name in nav_buttons:
            status = "✅ Detected" if button in detected_buttons else "❌ Not detected"
            print(f"{name}: {status}")

        # Report on color buttons
        print("\nColor Buttons:")
        for button, name in color_buttons:
            status = "✅ Detected" if button in detected_buttons else "❌ Not detected"
            print(f"{name}: {status}")
    else:
        print("\n❌ No buttons were detected during the test period.")


@pytest.fixture
def cec_listener():
    """Create and initialize a CEC listener for testing."""
    # Skip all real TV tests if NO_TV environment variable is set
    if os.environ.get("NO_TV"):
        pytest.skip("NO_TV environment variable set, skipping real TV tests")

    global detected_buttons, stop_listening, button_event, listener_thread

    # Reset detected buttons
    detected_buttons.clear()

    # Reset events
    button_event.clear()
    stop_listening.clear()

    # Create the adapter with a specific configuration
    config = CECConfig(
        device_name="PiTVRemote",
        physical_address="1.0.0.0",
        device_type=1,  # Recording device
    )
    adapter = CECAdapter(config=config)

    # Create a special handler that processes CEC events directly
    def handle_command(cmd, *args):
        global detected_buttons

        try:
            print(f"DEBUG: Command received: {cmd}, args: {args}")

            # For Format 4 which we're seeing in the logs
            if (
                isinstance(cmd, int)
                and cmd == 4
                and len(args) > 0
                and isinstance(args[0], dict)
            ):
                cmd_dict = args[0]
                opcode = cmd_dict.get("opcode")
                params = cmd_dict.get("parameters", b"")

                # User Control Pressed (0x44 or 68 decimal)
                if opcode == 68 and params and len(params) > 0:
                    button_code = params[0]
                    button_names = {
                        1: "UP",
                        2: "DOWN",
                        3: "LEFT",
                        4: "RIGHT",
                        0: "SELECT",
                        114: "RED",
                        113: "GREEN",
                        116: "YELLOW",
                        113: "BLUE",
                    }
                    button_name = button_names.get(
                        button_code, f"UNKNOWN (0x{button_code:02x})"
                    )
                    print(f"✅ TV REMOTE: {button_name} button (code: {button_code})")

                    # Add the button to detected buttons
                    detected_buttons.add(button_code)

                    # Signal that a button was pressed
                    button_event.set()
        except Exception as e:
            print(f"Error in command handler: {e}")
            import traceback

            traceback.print_exc()

    # Initialize the adapter
    if not adapter.init():
        pytest.skip("Failed to initialize CEC adapter - is a TV connected?")

    print("\n=== Setting up TV for Remote Control Test ===")

    # Step 1: Force TV power on with multiple attempts
    print("1. Turning on TV (sending multiple power-on commands)...")

    # First attempt
    adapter.power_on_tv()
    print("   Sent first power-on command")
    time.sleep(2)  # Wait for initial response

    # Second attempt to ensure TV is on
    adapter.power_on_tv()
    print("   Sent second power-on command")
    time.sleep(3)  # Wait longer for TV to fully power up

    # Send active source immediately after power on
    adapter.set_active_source()
    print("   Sent active source command")
    time.sleep(1)

    # Send one more power on command to be sure
    adapter.power_on_tv()
    print("   Sent final power-on command")
    time.sleep(1)

    # Step 2: Set as active source again
    print("2. Setting device as active source...")
    adapter.set_active_source()
    time.sleep(1)

    print("=== Setup complete, listening for remote button presses ===")
    print("Press UP, DOWN, LEFT, RIGHT, SELECT, or color buttons on your TV remote")

    # Register for key press events
    if hasattr(cec, "add_callback"):
        print("Registering direct CEC callbacks for button presses")
        cec.add_callback(handle_command, cec.EVENT_COMMAND)
        cec.add_callback(adapter.handle_keypress, cec.EVENT_KEYPRESS)

    # Add our command callback to detect user button presses (opcode 68 = 0x44 USER_CONTROL_PRESSED)
    adapter.add_command_callback(68, command_callback)

    # Add custom handler for FORMAT 4 commands
    def custom_event_handler(*args):
        handle_command(4, *args)

    adapter.add_command_callback(CECCommand.USER_CONTROL_PRESSED, custom_event_handler)

    # Start the thread that waits for button presses
    listener_thread = threading.Thread(target=wait_for_buttons_thread)
    listener_thread.daemon = True
    listener_thread.start()

    # Yield the adapter for testing
    yield adapter

    # Set the stop flag to signal the thread to exit
    stop_listening.set()

    print("Waiting for listener thread to finish...")
    # Wait for the thread to finish with a reasonable timeout
    listener_thread.join(timeout=2.0)

    # If thread is still alive after timeout, log a warning
    if listener_thread.is_alive():
        print("WARNING: Listener thread did not terminate within timeout")

    # Explicitly remove callbacks if possible
    if hasattr(cec, "remove_callback"):
        try:
            cec.remove_callback(handle_command, cec.EVENT_COMMAND)
            cec.remove_callback(adapter.handle_keypress, cec.EVENT_KEYPRESS)
            print("Removed CEC callbacks")
        except:
            print("Failed to remove CEC callbacks")

    # Clean up after the tests
    print("Cleaning up CEC adapter...")
    adapter.cleanup()

    # Make sure we finish callbacks before exiting
    print("Cleanup complete")


def test_detect_remote_buttons(cec_listener, request):
    """Test that detects buttons pressed on the real TV remote."""
    global stop_listening

    # Get the maximum wait time from environment variable or use default
    max_wait_time = int(os.environ.get("REMOTE_WAIT_TIME", "60"))

    # Inform the user about the test
    print(f"\n📺 Testing remote control button detection (timeout: {max_wait_time}s)")
    print(
        "📋 Looking for: UP, DOWN, LEFT, RIGHT, SELECT, RED, GREEN, YELLOW, BLUE buttons"
    )
    print("\n⚠️  IMPORTANT: Check that your TV is powered on!")
    print("   If the TV is not responding:")
    print("   1. Make sure the HDMI-CEC is enabled in your TV settings")
    print("   2. Try pressing the HOME button on your remote first")
    print("   3. If all else fails, manually power on the TV with its remote\n")

    # Wait for the wait_for_buttons_thread to complete
    start_time = time.time()

    try:
        while time.time() - start_time < max_wait_time and not stop_listening.is_set():
            # Give the user time to press buttons
            time.sleep(10)

            # If we've seen any buttons, we can exit early
            if len(detected_buttons) > 0:
                # We have detected at least one button
                print(f"✅ Detected at least one button: {detected_buttons}")
                break

            # Update on time remaining every 5 seconds
            elapsed = time.time() - start_time
            remaining = max_wait_time - elapsed
            if (
                remaining > 0
                and int(remaining) % 5 == 0
                and int(remaining) < max_wait_time
            ):
                print(f"⏱️  {int(remaining)} seconds remaining...")
    except KeyboardInterrupt:
        print("Test interrupted by user.")
        stop_listening.set()

    # Ensure we have at least one button press
    assert len(detected_buttons) > 0, "No buttons were detected during the test period"

    # Always print button summary
    print("\n📊 Button Detection Summary:")
    print(f"Total detected buttons: {len(detected_buttons)}")
    print(f"Button codes: {detected_buttons}")

    # Signal to stop the listener thread
    stop_listening.set()


if __name__ == "__main__":
    print("This file is intended to be run with pytest:")
    print("  pytest -xvs pi_tv_remote/tests/test_remote_listener.py")
    print()
    print("To adjust the wait time (default is 60 seconds):")
    print(
        "  REMOTE_WAIT_TIME=30 pytest -xvs pi_tv_remote/tests/test_remote_listener.py"
    )
    print()
    print("To skip all real TV tests (when no TV is connected):")
    print("  NO_TV=1 pytest -xvs pi_tv_remote/tests/test_remote_listener.py")
    print()
    print("Press Ctrl+C to exit the test at any time.")
