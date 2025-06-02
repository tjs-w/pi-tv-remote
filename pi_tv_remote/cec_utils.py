"""
CEC Utilities - functions to help with CEC operations across different environments.
"""

import importlib
import os
import platform
import sys
from typing import Any, Dict, Optional


def is_raspberry_pi() -> bool:
    """Check if the current system is a Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "raspberry pi" in f.read().lower()
    except:
        return False


def import_cec_constants(cec_module: Any) -> Dict[str, int]:
    """Import constants from the CEC module."""
    constants = {}

    # Device types
    device_constants = {
        "CECDEVICE_TV": 0,
        "CECDEVICE_RECORDING_DEVICE_1": 1,
        "CECDEVICE_RECORDING_DEVICE_2": 2,
        "CECDEVICE_TUNER_1": 3,
        "CECDEVICE_PLAYBACK_DEVICE_1": 4,
        "CECDEVICE_AUDIO_SYSTEM": 5,
        "CECDEVICE_TUNER_2": 6,
        "CECDEVICE_TUNER_3": 7,
        "CECDEVICE_PLAYBACK_DEVICE_2": 8,
        "CECDEVICE_RECORDING_DEVICE_3": 9,
        "CECDEVICE_TUNER_4": 10,
        "CECDEVICE_PLAYBACK_DEVICE_3": 11,
        "CECDEVICE_RESERVED_1": 12,
        "CECDEVICE_RESERVED_2": 13,
        "CECDEVICE_FREE_USE": 14,
        "CECDEVICE_BROADCAST": 15,
    }

    # Ensure all device constants exist
    for name, value in device_constants.items():
        constants[name] = value

    # Opcodes
    opcode_prefix = "CEC_OPCODE_"
    opcode_attrs = [
        "ACTIVE_SOURCE",
        "IMAGE_VIEW_ON",
        "TEXT_VIEW_ON",
        "INACTIVE_SOURCE",
        "REQUEST_ACTIVE_SOURCE",
        "ROUTING_CHANGE",
        "ROUTING_INFORMATION",
        "SET_STREAM_PATH",
        "STANDBY",
        "RECORD_OFF",
        "RECORD_ON",
        "RECORD_STATUS",
        "GIVE_PHYSICAL_ADDRESS",
        "REPORT_PHYSICAL_ADDRESS",
        "DEVICE_VENDOR_ID",
        "VENDOR_COMMAND",
        "VENDOR_COMMAND_WITH_ID",
        "VENDOR_REMOTE_BUTTON_DOWN",
        "GIVE_DEVICE_VENDOR_ID",
        "MENU_REQUEST",
        "MENU_STATUS",
        "GIVE_DEVICE_POWER_STATUS",
        "REPORT_POWER_STATUS",
        "GET_MENU_LANGUAGE",
        "SET_MENU_LANGUAGE",
        "DECK_CONTROL",
        "DECK_STATUS",
        "GIVE_DECK_STATUS",
        "PLAY",
        "GIVE_TUNER_DEVICE_STATUS",
        "SET_OSD_NAME",
        "GIVE_OSD_NAME",
        "SET_OSD_STRING",
        "SET_TIMER_PROGRAM_TITLE",
        "USER_CONTROL_PRESSED",
        "USER_CONTROL_RELEASE",
        "GIVE_OSD_NAME",
        "FEATURE_ABORT",
    ]

    # Event types
    event_constants = {
        "EVENT_LOG": 0x01,
        "EVENT_KEYPRESS": 0x02,
        "EVENT_COMMAND": 0x04,
        "EVENT_ALL": 0xFF,
    }

    for name, value in event_constants.items():
        constants[name] = value

    # User control codes/Remote buttons
    remote_button_constants = {
        "CEC_USER_CONTROL_SELECT": 0x00,
        "CEC_USER_CONTROL_UP": 0x01,
        "CEC_USER_CONTROL_DOWN": 0x02,
        "CEC_USER_CONTROL_LEFT": 0x03,
        "CEC_USER_CONTROL_RIGHT": 0x04,
        "CEC_USER_CONTROL_EXIT": 0x0D,
        "CEC_USER_CONTROL_VOLUME_UP": 0x41,
        "CEC_USER_CONTROL_VOLUME_DOWN": 0x42,
        "CEC_USER_CONTROL_MUTE": 0x43,
        "CEC_USER_CONTROL_PLAY": 0x44,
        "CEC_USER_CONTROL_STOP": 0x45,
        "CEC_USER_CONTROL_PAUSE": 0x46,
        "CEC_USER_CONTROL_RECORD": 0x47,
        "CEC_USER_CONTROL_REWIND": 0x48,
        "CEC_USER_CONTROL_FAST_FORWARD": 0x49,
    }

    for name, value in remote_button_constants.items():
        constants[name] = value

    # Try to get constants from the CEC module first
    for attr in dir(cec_module):
        if (
            attr.startswith("CECDEVICE_")
            or attr.startswith("CEC_OPCODE_")
            or attr.startswith("CEC_USER_CONTROL_")
            or attr.startswith("EVENT_")
        ):
            constants[attr] = getattr(cec_module, attr)

    return constants


def get_cec_module():
    """
    Get the CEC module, providing fallbacks for missing constants.

    Returns:
        The CEC module
    """
    # Try to import the real CEC module
    try:
        cec = importlib.import_module("cec")
        print("Using CEC module")

        # Import and set constants from the real module
        constants = import_cec_constants(cec)

        # Add device constants if missing
        device_constants = {
            "CECDEVICE_TV": 0,
            "CECDEVICE_RECORDING_DEVICE_1": 1,
            "CECDEVICE_RECORDING_DEVICE_2": 2,
            "CECDEVICE_TUNER_1": 3,
            "CECDEVICE_PLAYBACK_DEVICE_1": 4,
            "CECDEVICE_AUDIO_SYSTEM": 5,
            "CECDEVICE_TUNER_2": 6,
            "CECDEVICE_TUNER_3": 7,
            "CECDEVICE_PLAYBACK_DEVICE_2": 8,
            "CECDEVICE_RECORDING_DEVICE_3": 9,
            "CECDEVICE_TUNER_4": 10,
            "CECDEVICE_PLAYBACK_DEVICE_3": 11,
            "CECDEVICE_RESERVED_1": 12,
            "CECDEVICE_RESERVED_2": 13,
            "CECDEVICE_FREE_USE": 14,
            "CECDEVICE_BROADCAST": 15,
        }

        # Add any missing device constants
        for name, value in device_constants.items():
            if not hasattr(cec, name):
                setattr(cec, name, value)
                print(f"Added missing device constant {name} = {value}")

        # Ensure event constants exist
        event_constants = {
            "EVENT_LOG": 0x01,
            "EVENT_KEYPRESS": 0x02,
            "EVENT_COMMAND": 0x04,
            "EVENT_ALL": 0xFF,
        }

        # Add any missing event constants
        for name, value in event_constants.items():
            if not hasattr(cec, name):
                setattr(cec, name, value)
                print(f"Added missing event constant {name} = {value}")

        return cec

    except ImportError:
        print("\nERROR: CEC module not installed")
        print("Pi TV Remote requires the 'cec' package to function.")

        if is_raspberry_pi():
            print("\nInstallation instructions for Raspberry Pi:")
            print("1. Install libcec development libraries:")
            print("   sudo apt-get update")
            print("   sudo apt-get install libcec-dev python3-dev build-essential")
            print("2. Install the Python CEC module:")
            print("   pip install cec")
        else:
            print("\nThis package is primarily intended for use on Raspberry Pi.")
            print("It requires CEC hardware support to function.")

        print("\nNOTE: Pi TV Remote requires CEC hardware support to function.")

        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: CEC module failed to initialize: {e}")
        print("This could indicate missing hardware or misconfigured CEC drivers.")

        if not is_raspberry_pi():
            print("\nNOTE: You are running on a non-Raspberry Pi system.")
            print("Pi TV Remote requires actual CEC hardware to function properly.")

        sys.exit(1)
