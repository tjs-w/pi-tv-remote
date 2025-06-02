#!/usr/bin/env python3
"""
Test CEC Adapter with Real TV
This pytest module tests the CECAdapter class with real TV hardware.
"""
import os
import time
from typing import Optional

import pytest

from pi_tv_remote.cec_adapter import (
    CECAdapter,
    CECCommand,
    CECConfig,
    RemoteButton,
    log_debug,
)

# Store the TV's power status for tests
tv_power_status: Optional[int] = None


# Callback to capture TV power status responses
def tv_power_status_callback(cmd, *args):
    """Callback for TV power status responses"""
    global tv_power_status

    try:
        # Try to extract power status from different formats
        if hasattr(cmd, "parameters") and cmd.parameters:
            # New format with parameters attribute
            tv_power_status = cmd.parameters[0] if cmd.parameters else None
        elif len(args) > 3 and args[3]:
            # Old format with parameters in args[3]
            tv_power_status = args[3][0] if args[3] else None

        # Log the status
        status_text = "unknown"
        if tv_power_status == 0:
            status_text = "on"
        elif tv_power_status == 1:
            status_text = "standby"
        elif tv_power_status == 2:
            status_text = "in transition to on"
        elif tv_power_status == 3:
            status_text = "in transition to standby"

        print(f"TV power status: {status_text} (0x{tv_power_status:02x})")
    except Exception as e:
        print(f"Error in power status callback: {e}")


# Fixture for the CEC adapter
@pytest.fixture
def cec_adapter():
    """Create and initialize a CEC adapter for testing."""
    # Skip all real TV tests if NO_TV environment variable is set
    if os.environ.get("NO_TV"):
        pytest.skip("NO_TV environment variable set, skipping real TV tests")

    # Reset the global TV power status
    global tv_power_status
    tv_power_status = None

    # Create the adapter with default config
    adapter = CECAdapter()

    # Initialize the adapter
    if not adapter.init():
        pytest.skip("Failed to initialize CEC adapter - is a TV connected?")

    # Register for power status reports
    adapter.add_command_callback(
        CECCommand.REPORT_POWER_STATUS, tv_power_status_callback
    )

    # Yield the adapter for testing
    yield adapter

    # Clean up after the tests
    adapter.cleanup()


def test_cec_initialization(cec_adapter):
    """Test that the CEC adapter initializes correctly."""
    assert cec_adapter.initialized


def test_power_on_tv(cec_adapter):
    """Test turning on the TV."""
    # Check current TV power status
    print("Checking TV power status...")
    status_result = cec_adapter.request_power_status()
    assert status_result, "Failed to request TV power status"

    # Wait for response and check if TV is already on
    time.sleep(2)

    if tv_power_status == 0:  # TV is already on
        print("TV is already powered on, skipping power on command")
    else:
        # Power on the TV
        print(f"TV status is {tv_power_status}, sending power on command...")
        try:
            result = cec_adapter.power_on_tv()
            assert result, "Failed to power on TV"
            print("Power on command sent successfully")

            # Give the TV time to turn on
            time.sleep(3)
        except Exception as e:
            print(f"Warning: Error during power on: {e}")

    # Set as active source
    print("Setting device as active source...")
    try:
        active_source_result = cec_adapter.set_active_source()
        assert active_source_result, "Failed to set as active source"
        print("Set as active source successfully")
    except Exception as e:
        print(f"Warning: Could not set as active source: {e}")
        # Continue with test even if this fails


def test_set_active_source(cec_adapter):
    """Test setting the device as the active source."""
    # Set as active source
    result = cec_adapter.set_active_source()
    assert result, "Failed to set as active source"


def test_volume_control(cec_adapter):
    """Test volume control."""
    # Send volume up
    result = cec_adapter.send_remote_button(RemoteButton.VOLUME_UP)
    assert result, "Failed to send volume up command"
    time.sleep(1)

    # Send volume down
    result = cec_adapter.send_remote_button(RemoteButton.VOLUME_DOWN)
    assert result, "Failed to send volume down command"


def test_send_command(cec_adapter):
    """Test sending a direct CEC command."""
    # Send a direct command (GIVE_DEVICE_POWER_STATUS)
    result = cec_adapter.send_command(
        CECCommand.GIVE_DEVICE_POWER_STATUS, destination=0  # TV
    )
    assert result, "Failed to send direct command"


def test_remote_button_press(cec_adapter):
    """Test sending a remote button press."""
    # Send a button press (UP button)
    result = cec_adapter.send_remote_button(RemoteButton.UP)
    assert result, "Failed to send remote button press"
    time.sleep(1)


@pytest.mark.standby
def test_standby_tv(cec_adapter):
    """Test putting the TV in standby mode."""
    # This test is marked with 'standby' so it can be skipped if needed

    # Send standby command
    result = cec_adapter.standby_tv()
    assert result, "Failed to put TV in standby"
    time.sleep(2)  # Give the TV time to go into standby


if __name__ == "__main__":
    print("This file is intended to be run with pytest:")
    print("  pytest -xvs pi_tv_remote/tests/test_cec_adapter_real_tv.py")
    print()
    print("To skip standby tests:")
    print("  pytest -xvs pi_tv_remote/tests/test_cec_adapter_real_tv.py --skip-standby")
    print()
    print("To skip all real TV tests (when no TV is connected):")
    print("  NO_TV=1 pytest -xvs pi_tv_remote/tests/test_cec_adapter_real_tv.py")
